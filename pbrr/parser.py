import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import feedparser
import requests
from bs4 import BeautifulSoup

from pbrr.log import Log
from pbrr.parsed_feed_item import ParsedFeedItem
from pbrr.parsed_feed_site import ParsedFeedSite
from pbrr.settings import Settings


class Parser:

    KEY_SITE = "site"
    KEY_ENTRIES = "entries"
    KEY_CATEGORY = "category"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def fetch_sites_metadata(self, opml_filename: str) -> List[Tuple[str, Optional[str], Optional[str]]]:
        opml_filepath = os.path.join(self.settings.base_output_path, opml_filename)

        def site_outline(element: Any) -> bool:
            return all(
                [
                    element.name == "outline",
                    element.has_attr("xmlUrl"),
                    element.has_attr("type"),
                    element.get("type", "") == "rss",
                ]
            )

        def site_category(element: Any) -> Optional[str]:
            parent = element.findParent()
            if parent.name == "outline" and parent.has_attr("title"):
                return parent.get("title")
            else:
                return None

        if not os.path.exists(opml_filepath):
            Log.error_and_exit("OPML file '{}' not found".format(opml_filepath))

        with open(opml_filepath, encoding="utf-8") as opml_file_handle:
            xml_contents = opml_file_handle.read()
        soup = BeautifulSoup(xml_contents, "xml")
        sites = soup.opml.body.findAll(site_outline)

        return [
            (site["xmlUrl"], site.get("title"), site_category(site))
            for site in sites
            if not any([True for skip_url in self.settings.skip_urls if site["xmlUrl"].startswith(skip_url)])
        ]

    def fetch_site(
        self, url: str, title: Optional[str], category: Optional[str]
    ) -> Dict[str, Union[ParsedFeedSite, List[ParsedFeedItem]]]:
        try:
            feed_response = requests.get(
                url,
                headers={
                    "User-Agent": "pbrr/1.0 (https://github.com/Kartones/pbrr)",
                    "If-Modified-Since": self._format_if_modified_header(self.settings.last_fetch_mark),
                },
                timeout=15,
            )
            source_site = feedparser.parse(feed_response.text)
        except (Exception) as e:
            # else need to directly catch urllib errors
            if "Name or service not known" in str(e):
                Log.warn_and_raise_error("{title} ({url}) skipped, error fetching url".format(title=title, url=url))
            else:
                Log.warn("{title} ({url}) skipped. Error: {error}".format(title=title, url=url, error=e))
                raise ValueError(str(e))

        # don't override, leave content as it is
        if feed_response.status_code == 304:
            return self._not_modified_site(title, category)

        self._log_and_error_if_proceeds(
            url=url, title=title, source_site=source_site, response_status_code=feed_response.status_code
        )

        parsed_site = self._parse_site(feed=source_site.feed, provided_title=title, category=category)

        entries_count = len(source_site.entries) - 1

        parsed_entries = [
            self._parse_entry(entry=entry, parsed_site=parsed_site, entry_reverse_index=(entries_count - index))
            for index, entry in enumerate(source_site.entries)
        ]

        if parsed_entries:
            parsed_entries = self._filter_entries(parsed_entries)

            # reorder by most recent first (seen inverse order)
            parsed_entries = sorted(parsed_entries, key=lambda s: (s.published), reverse=True)
            # correct site last update time with latest entry (some sites report incorrectly or not even have)
            parsed_site.last_updated = parsed_entries[0].published
            # and cut to a reasonable limit (seen also feeds with full dumps maybe? of content)
            parsed_entries = parsed_entries[:15]

        Log.info("> Fetched: {title}".format(title=title))

        return {self.KEY_SITE: parsed_site, self.KEY_ENTRIES: parsed_entries}

    def _filter_entries(self, entries: List[ParsedFeedItem]) -> List[ParsedFeedItem]:
        return [
            entry
            for entry in entries
            if not any([True for title in self.settings.skip_filters if title in entry.title])
        ]

    # from feedparser source
    # https://github.com/kurtmckee/feedparser/blob/bae53018cd99520e2be1b96e7d51bd5799b02ac9/feedparser/http.py#L95
    @staticmethod
    def _format_if_modified_header(modified: Any) -> Optional[str]:
        if isinstance(modified, datetime):
            modified = modified.utctimetuple()
        if modified:
            short_weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
                short_weekdays[modified[6]],
                modified[2],
                months[modified[1] - 1],
                modified[0],
                modified[3],
                modified[4],
                modified[5],
            )
        else:
            return None

    @staticmethod
    def _log_and_error_if_proceeds(url: str, title: Optional[str], source_site: Any, response_status_code: int) -> None:
        # just warn, don't skip
        if "bozo" in source_site.keys() and source_site["bozo"] == 1 and response_status_code != 200:
            Log.info(
                "{title} ({url}) bozo=1 http_status:{status}".format(title=title, url=url, status=response_status_code)
            )

        # should always skip by raising error
        if (
            not source_site.feed.keys()
            or "link" not in source_site.feed.keys()
            or response_status_code in [401, 403, 404]
        ):
            Log.warn_and_raise_error(
                "{title} ({url}) skipped, feed malformed/not retrieved. HTTPStatus: {status}".format(
                    title=title,
                    url=url,
                    status=response_status_code,
                )
            )

        if response_status_code in [301]:
            Log.warn(
                "{title} ({url}) has moved ({status}) Check new URL".format(
                    title=title, url=url, status=response_status_code
                )
            )

        if response_status_code in [410]:
            Log.warn_and_raise_error(
                "{title} ({url}) skipped, received http_status:{status} Url gone".format(
                    title=title, url=url, status=response_status_code
                )
            )

    @classmethod
    def _not_modified_site(
        cls, title: Optional[str], category: Optional[str]
    ) -> Dict[str, Union[ParsedFeedSite, List[ParsedFeedItem]]]:
        return {cls.KEY_SITE: cls._parse_site(feed=None, provided_title=title, category=category), cls.KEY_ENTRIES: []}

    @classmethod
    def _parse_site(cls, feed: Optional[Any], provided_title: Optional[str], category: Optional[str]) -> ParsedFeedSite:
        if not feed:
            return ParsedFeedSite(
                title=cls._sanitize_site_title(feed=None, provided_title=provided_title),
                category=category,
                link=None,
                last_updated=None,
            )
        else:
            return ParsedFeedSite(
                title=cls._sanitize_site_title(feed=feed, provided_title=provided_title),
                category=category,
                link=feed.link,
                # field set later, unreliable from main feed
                last_updated=None,
            )

    @classmethod
    def _parse_entry(cls, entry: Any, parsed_site: ParsedFeedSite, entry_reverse_index: int) -> ParsedFeedItem:
        content = ""
        content_key = None
        is_array = False

        # seen some entries on same site with and without summary_detail, so can't just sample and apply to all
        if "content" in entry.keys():
            content_key = "content"
            is_array = True
        elif "summary_detail" in entry.keys():
            content_key = "summary_detail"
        elif "title_detail" in entry.keys():
            content_key = "title_detail"

        if content_key:
            if is_array:
                content_by_type = [content.value for content in entry[content_key] if content.type == "text/html"]
                if not content_by_type:
                    content_by_type = [content.value for content in entry[content_key] if content.type == "text/plain"]
                content = content_by_type[0] if content_by_type else ""
            else:
                content = entry[content_key].value

        published = cls._published_field_from(entry=entry, entry_reverse_index=entry_reverse_index)

        return ParsedFeedItem(
            title=entry.title, link=entry.link, published=published, content=content, parent=parsed_site
        )

    @staticmethod
    def _published_field_from(entry: Any, entry_reverse_index: int) -> datetime:
        if "published" in entry.keys():
            published = entry.published_parsed if "published_parsed" in entry.keys() else entry.published
        elif "updated" in entry.keys():
            published = entry.updated_parsed if "updated_parsed" in entry.keys() else entry.updated
        else:
            # fake some time to avoid collisions when generating files
            published = time.gmtime(entry_reverse_index * 60)

        published_datetime = datetime.fromtimestamp(time.mktime(published))
        # use seconds as a way to differentiate each entry, so if two are published at the same time, don't collide
        published_datetime = published_datetime + timedelta(seconds=entry_reverse_index)

        return published_datetime

    @staticmethod
    def _sanitize_site_title(feed: Any, provided_title: Optional[str]) -> str:
        if provided_title:
            return provided_title
        elif not feed or "title" not in feed.keys():
            return "untitled{ts}".format(ts=time.time_ns())
        else:
            return feed.title.encode("utf-8", errors="ignore").decode()

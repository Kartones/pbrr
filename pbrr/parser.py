import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import feedparser
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
            source_site = feedparser.parse(
                url, agent="pbrr/0.2 (https://github.com/Kartones/pbrr)", modified=self.settings.last_fetch_mark
            )
        except Exception as e:
            # else need to directly catch urllib errors
            if "Name or service not known" in str(e):
                Log.warn_and_raise_error("{title} ({url}) skipped, error fetching url".format(title=title, url=url))
            else:
                Log.warn(
                    "{title} ({url}) skipped. Error: {error} Headers: {headers}".format(
                        title=title,
                        url=url,
                        error=e,
                        headers=",".join(
                            ["{}={}".format(key, source_site.headers[key]) for key in source_site.headers.keys()]
                        ),
                    )
                )
                raise e

        # don't override, leave content as it is
        if source_site.status == 304:
            return self._not_modified_site(title, category)

        self._log_and_error_if_proceeds(url=url, title=title, source_site=source_site)

        parsed_site = self._parse_site(feed=source_site.feed, provided_title=title, category=category)

        parsed_entries = []  # type: List[ParsedFeedItem]
        for entry in source_site.entries:
            parsed_entries.append(self._parse_entry(entry=entry, parsed_site=parsed_site))

        # reorder by most recent first (seen inverse order)
        parsed_entries = sorted(parsed_entries, key=lambda s: (s.published), reverse=True)
        # correct site last update time with latest entry if needed (some sites report incorrectly or not even have)
        if parsed_site.last_updated == time.gmtime(0) or parsed_entries[0].published < parsed_site.last_updated:
            parsed_site.last_updated = parsed_entries[0].published

        Log.info("> Fetched: {title}".format(title=title))

        return {self.KEY_SITE: parsed_site, self.KEY_ENTRIES: parsed_entries}

    @staticmethod
    def _log_and_error_if_proceeds(url: str, title: Optional[str], source_site: Any) -> None:
        # just warn, don't skip
        if "bozo" in source_site.keys() and source_site["bozo"] == 1 and source_site.status != 200:
            Log.info(
                "{title} ({url}) bozo=1 http_status:{status}".format(title=title, url=url, status=source_site.status)
            )

        # should always skip by raising error
        if (
            not source_site.feed.keys()
            or "link" not in source_site.feed.keys()
            or source_site.status in [401, 403, 404]
        ):
            Log.warn_and_raise_error(
                "{title} ({url}) skipped, feed malformed or not retrieved. HTTP Status: {status} Headers: {headers}".format(
                    title=title,
                    url=url,
                    status=source_site.status,
                    headers=",".join(
                        ["{}={}".format(key, source_site.headers[key]) for key in source_site.headers.keys()]
                    ),
                )
            )

        if source_site.status in [301]:
            Log.warn(
                "{title} ({url}) has moved ({status}) Check new URL".format(
                    title=title, url=url, status=source_site.status
                )
            )

        if source_site.status in [410]:
            Log.warn_and_raise_error(
                "{title} ({url}) skipped, received http_status:{status} Url gone".format(
                    title=title, url=url, status=source_site.status
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

        last_updated = None
        # Seen feeds without any date at all, and keeping things simple, if can't parse, assume not present
        if "updated_parsed" in feed.keys():
            last_updated = feed.updated_parsed
        elif "published_parsed" in feed.keys():
            last_updated = feed.published_parsed

        if not last_updated:
            last_updated = time.gmtime(0)

        return ParsedFeedSite(
            title=cls._sanitize_site_title(feed=feed, provided_title=provided_title),
            category=category,
            link=feed.link,
            last_updated=last_updated,
        )

    @classmethod
    def _parse_entry(cls, entry: Any, parsed_site: ParsedFeedSite) -> ParsedFeedItem:
        content = ""
        content_key = None
        is_array = False

        # seen some entries on same site with and without summary_detail, so can't just sample and apply to all
        if "content" in entry.keys():
            content_key = "content"
            is_array = True
        elif "summary_detail" in entry.keys():
            content_key = "summary_detail"

        if content_key:
            if is_array:
                content = [content.value for content in entry[content_key] if content.type == "text/html"][0]
            else:
                content = entry[content_key].value

        published = cls._published_field_from(entry)

        return ParsedFeedItem(
            title=entry.title, link=entry.link, published=published, content=content, parent=parsed_site
        )

    @staticmethod
    def _published_field_from(entry: Any) -> Optional[time.struct_time]:
        if "published" in entry.keys():
            published = entry.published_parsed if "published_parsed" in entry.keys() else entry.published
        elif "updated" in entry.keys():
            published = entry.updated_parsed if "updated_parsed" in entry.keys() else entry.updated
        else:
            published = None

        return published

    @staticmethod
    def _sanitize_site_title(feed: Any, provided_title: Optional[str]) -> str:
        if provided_title:
            return provided_title
        elif not feed or "title" not in feed.keys():
            return "untitled{ts}".format(ts=time.time_ns())
        else:
            return feed.title.encode("utf-8", errors="ignore").decode()

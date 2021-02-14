import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import feedparser
from bs4 import BeautifulSoup

from pbrr.log import Log
from pbrr.parsed_feed_item import ParsedFeedItem
from pbrr.parsed_feed_site import ParsedFeedSite


# TODO: pretty aggressive skipping encoding errors, make more flexible once everything working
class Parser:

    KEY_SITE = "site"
    KEY_ENTRIES = "entries"

    def __init__(self, base_input_path: str) -> None:
        self.base_input_path = base_input_path

    def fetch_sites_metadata(self, opml_filename: str) -> List[Tuple[str, Optional[str]]]:
        opml_filepath = os.path.join(self.base_input_path, opml_filename)

        # TODO: worth checking that type="rss"?
        def site_outline(element: Any) -> bool:
            return element.name == "outline" and element.has_attr("xmlUrl")

        if not os.path.exists(opml_filepath):
            Log.error_and_exit("OPML file '{}' not found".format(opml_filepath))

        with open(opml_filepath, encoding="utf-8") as opml_file_handle:
            xml_contents = opml_file_handle.read()
        soup = BeautifulSoup(xml_contents, "xml")
        sites = soup.opml.body.findAll(site_outline)

        return [(site["xmlUrl"], site.get("title")) for site in sites]

    @classmethod
    def parse(cls, url: str, title: Optional[str]) -> Dict[str, Union[ParsedFeedSite, List[ParsedFeedItem]]]:
        try:
            source_site = feedparser.parse(url, agent="pbrr/0.2 (https://github.com/Kartones/pbrr)")
        except Exception as e:
            # else need to directly catch urllib errors
            if "Name or service not known" in str(e):
                Log.warn_and_raise_error("{title} ({url}) skipped, error fetching url".format(title=title, url=url))
            else:
                Log.warn("{title} ({url}) skipped. Error: {error}".format(title=title, url=url, error=e))
                raise e

        # not worth of skipping
        if "bozo" in source_site.keys() and source_site["bozo"] == 1 and source_site.status != 200:
            Log.info(
                "{title} ({url}) bozo=1 http_status:{status}".format(title=title, url=url, status=source_site.status)
            )
        if source_site.status in [301]:
            Log.warn(
                "{title} ({url}) has moved ({status}) Check new URL".format(
                    title=title, url=url, status=source_site.status
                )
            )

        # should always skip
        if not source_site.feed.keys() or "link" not in source_site.feed.keys():
            Log.warn_and_raise_error(
                "{title} ({url}) skipped, feed malformed or not retrieved".format(title=title, url=url)
            )
        if source_site.status in [410]:
            Log.warn_and_raise_error(
                "{title} ({url}) skipped, received http_status:{status} Check new URL".format(
                    title=title, url=url, status=source_site.status
                )
            )

        parsed_site = cls._parse_site(feed=source_site.feed, provided_title=title)

        parsed_entries = []  # type: List[ParsedFeedItem]
        for entry in source_site.entries:
            parsed_entries.append(cls._parse_entry(entry=entry, parsed_site=parsed_site))

        Log.info("> Fetched: {title}".format(title=title))

        return {cls.KEY_SITE: parsed_site, cls.KEY_ENTRIES: parsed_entries}

    @classmethod
    def _parse_site(cls, feed: Any, provided_title: Optional[str]) -> ParsedFeedSite:
        # Seen feeds without any date at all
        if "updated" in feed.keys():
            last_updated = feed.updated_parsed if "updated_parsed" in feed.keys() else feed.updated
        elif "published" in feed.keys():
            last_updated = feed.published_parsed if "published_parsed" in feed.keys() else feed.published
        else:
            last_updated = ""

        return ParsedFeedSite(
            title=cls._sanitize_site_title(feed=feed, provided_title=provided_title),
            link=feed.link,
            last_updated=last_updated,
        )

    @staticmethod
    def _parse_entry(entry: Any, parsed_site: ParsedFeedSite) -> ParsedFeedItem:
        # seen some entries on same site with and without summary_detail, so can't just sample and apply to all
        no_content = False
        if "content" in entry.keys():
            content_key = "content"
            is_array = True
        elif "summary_detail" in entry.keys():
            content_key = "summary_detail"
            is_array = False
        else:
            no_content = True

        if no_content:
            content = ""
        else:
            if is_array:
                content = [
                    content.value.encode("cp1252", errors="ignore").decode("UTF-8", errors="ignore")
                    for content in entry[content_key]
                    if content.type == "text/html"
                ][0]
            else:
                content = entry[content_key].value.encode("cp1252", errors="ignore").decode("UTF-8", errors="ignore")

        if "published" in entry.keys():
            published = entry.published_parsed if "published_parsed" in entry.keys() else entry.published
        elif "updated" in entry.keys():
            published = entry.updated_parsed if "updated_parsed" in entry.keys() else entry.updated
        else:
            published = None

        return ParsedFeedItem(
            title=entry.title, link=entry.link, published=published, content=content, parent=parsed_site
        )

    @staticmethod
    def _sanitize_site_title(feed: Any, provided_title: Optional[str]) -> str:
        if provided_title:
            return provided_title
        elif "title" not in feed.keys():
            return "untitled{ts}".format(ts=time.time_ns())
        else:
            return feed.title.encode("utf-8", errors="ignore").decode()

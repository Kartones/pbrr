import os
import time
from typing import List, Optional, Tuple

from pbrr.parsed_feed_item import ParsedFeedItem
from pbrr.parsed_feed_site import ParsedFeedSite


class Writer:

    ENTRY_HTML_TEMPLATE = """
<h2><a href=\"{link}\">{title}</a></h2><br/>
<span class=\"publish-date\">{published}</span<br/>
<div class=\"content\">{content}</div>
"""

    ENTRIES_LIST_HTML_TEMPLATE = """
<ul>{entries}</ul>
"""
    ENTRIES_LIST_ITEM_HTML_TEMPLATE = """
<li><a href=\"{relative_path}\">{title}</a> <span class=\"publish-date\">{published}</span></li>
"""

    SITES_LIST_HTML_TEMPLATE = """
<ul>{sites}</ul>
"""

    SITES_LIST_ITEM_HTML_TEMPLATE = """
<li><a href=\"{relative_path}\">{title}</a> <span class=\"last-update-date\">{last_update}</span></li>
"""

    def __init__(self, base_output_path: str) -> None:
        self.base_output_path = base_output_path
        self.enqueued_data = []  # type: List[Tuple[ParsedFeedSite, List[ParsedFeedItem]]]

    def enqueue(self, site: ParsedFeedSite, entries: List[ParsedFeedItem]) -> None:
        self.enqueued_data.append((site, entries))

    def save(self) -> None:
        self._ensure_base_path()

        enqueued_sites = []  # type: List[ParsedFeedSite]

        for (
            site,
            entries,
        ) in self.enqueued_data:
            self._save_site(site)
            self._save_entries(entries, site)
            self._save_entries_list(entries, site)
            enqueued_sites.append(site)
        self.enqueued_data.clear()

        enqueued_sites = self._sort_sites_list_by_last_updated(enqueued_sites)
        self._save_sites_list(enqueued_sites)
        enqueued_sites.clear()

    def _save_site(self, site: ParsedFeedSite) -> None:
        if not os.path.exists(self._site_path(site)):
            os.mkdir(self._site_path(site))

    def _save_entries(self, entries: List[ParsedFeedItem], site: ParsedFeedSite) -> None:
        for entry in entries:
            entry_filename = os.path.join(self._site_path(site), entry.html_filename)
            with open(entry_filename, "w") as entry_file_handle:
                entry_file_handle.write(
                    self.ENTRY_HTML_TEMPLATE.format(
                        title=entry.title,
                        link=entry.link,
                        published=self._stringified_date(entry.published),
                        content=entry.content,
                    )
                )

    def _save_entries_list(self, entries: List[ParsedFeedItem], site: ParsedFeedSite) -> None:
        entries_markup = "\n".join(
            [
                self.ENTRIES_LIST_ITEM_HTML_TEMPLATE.format(
                    relative_path=entry.html_filename,
                    title=entry.title,
                    published=self._stringified_date(entry.published),
                )
                for entry in entries
            ]
        )

        with open(os.path.join(self._site_path(site), "index.html"), "w") as entries_list_file_handle:
            entries_list_file_handle.write(self.ENTRIES_LIST_HTML_TEMPLATE.format(entries=entries_markup))

    def _sort_sites_list_by_last_updated(self, sites: List[ParsedFeedSite]) -> List[ParsedFeedSite]:
        return sorted(sites, key=lambda s: time.mktime(s.last_updated) if s.last_updated else 0, reverse=True)

    def _save_sites_list(self, sites: List[ParsedFeedSite]) -> None:
        sites_markup = "\n".join(
            [
                self.SITES_LIST_ITEM_HTML_TEMPLATE.format(
                    relative_path="{folder}/index.html".format(folder=site.title_for_filename),
                    title=site.title,
                    last_update=self._stringified_date(site.last_updated),
                )
                for site in sites
            ]
        )

        with open(os.path.join(self.base_output_path, "index.html"), "w") as sites_list_file_handle:
            sites_list_file_handle.write(self.SITES_LIST_HTML_TEMPLATE.format(sites=sites_markup))

    def _ensure_base_path(self) -> None:
        if not os.path.exists(self.base_output_path):
            os.mkdir(self.base_output_path)

    def _site_path(self, site: ParsedFeedSite) -> str:
        return os.path.join(self.base_output_path, site.title_for_filename)

    @staticmethod
    def _stringified_date(original_date: Optional[time.struct_time]) -> str:
        return (
            "{year:04d}-{month:02d}-{day:02d} {hour:02d}:{mins:02d}".format(
                year=original_date.tm_year,
                month=original_date.tm_mon,
                day=original_date.tm_mday,
                hour=original_date.tm_hour,
                mins=original_date.tm_min,
            )
            if original_date
            else ""
        )

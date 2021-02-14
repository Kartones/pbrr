import os
import time
from distutils.dir_util import copy_tree
from typing import List, Optional, Tuple

from pbrr.parsed_feed_item import ParsedFeedItem
from pbrr.parsed_feed_site import ParsedFeedSite


class Writer:
    def __init__(self, base_output_path: str) -> None:
        self.base_output_path = base_output_path
        self.enqueued_data = []  # type: List[Tuple[ParsedFeedSite, List[ParsedFeedItem]]]

    def enqueue(self, site: ParsedFeedSite, entries: List[ParsedFeedItem]) -> None:
        self.enqueued_data.append((site, entries))

    def save(self) -> None:
        self._ensure_base_path()

        self._copy_template_required_files_if_needed()

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
                    self._load_template("entry").format(
                        title=entry.title,
                        link=entry.link,
                        back_link="{folder}/index.html".format(folder=site.title_for_filename),
                        published=self._stringified_date(entry.published),
                        content=entry.content,
                    )
                )

    def _save_entries_list(self, entries: List[ParsedFeedItem], site: ParsedFeedSite) -> None:
        entries_markup = "\n".join(
            [
                self._load_template("entries_list_item").format(
                    relative_path="{folder}/{file}".format(folder=site.title_for_filename, file=entry.html_filename),
                    title=entry.title,
                    published=self._stringified_date(entry.published),
                )
                for entry in entries
            ]
        )

        with open(os.path.join(self._site_path(site), "index.html"), "w") as entries_list_file_handle:
            entries_list_file_handle.write(self._load_template("entries_list").format(entries=entries_markup))

    def _sort_sites_list_by_last_updated(self, sites: List[ParsedFeedSite]) -> List[ParsedFeedSite]:
        return sorted(sites, key=lambda s: time.mktime(s.last_updated) if s.last_updated else 0, reverse=True)

    def _save_sites_list(self, sites: List[ParsedFeedSite]) -> None:
        sites_markup = "\n".join(
            [
                self._load_template("sites_list_item").format(
                    relative_path="{folder}/index.html".format(folder=site.title_for_filename),
                    title=site.title,
                    last_update=self._stringified_date(site.last_updated),
                )
                for site in sites
            ]
        )

        with open(os.path.join(self.base_output_path, "index.html"), "w") as sites_list_file_handle:
            sites_list_file_handle.write(self._load_template("index").format(sites=sites_markup))

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

    @staticmethod
    def _load_template(template_name: str) -> str:
        with open(os.path.join("pbrr", "templates", "{name}.html".format(name=template_name))) as template_file_handle:
            return template_file_handle.read()

    # Note that it won't check individual file presence, nor differences in content. If they get updated, just delete
    # and let it re-create corresponding folder with new files
    def _copy_template_required_files_if_needed(self) -> None:
        for folder in ["css", "fonts", "js"]:
            path = os.path.join(self.base_output_path, folder)
            if not os.path.exists(path):
                copy_tree(os.path.join("pbrr", "templates", folder), path)

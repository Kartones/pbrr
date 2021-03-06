import os
from collections import defaultdict
from datetime import datetime
from distutils.dir_util import copy_tree
from typing import List, Tuple

from pbrr.parsed_feed_item import ParsedFeedItem
from pbrr.parsed_feed_site import ParsedFeedSite
from pbrr.settings import Settings

MAIN_TEMPLATE = "index"
MAIN_SITES_LIST_ITEM_TEMPLATE = "sites_list_item"
ENTRIES_LIST_TEMPLATE = "entries_list"
ENTRIES_LIST_ITEM_TEMPLATE = "entries_list_item"
ENTRY_TEMPLATE = "entry"
SITES_CATEGORY_TEMPLATE = "sites_category"

BASE_FOLDER = "pbrr"
TEMPLATES_FOLDER = "templates"

NO_CATEGORY_TITLE = "Uncategorized"


class Writer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
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
            if entries:
                self._save_site(site)
                self._save_entries(entries, site)
                self._save_entries_list(entries, site)
            enqueued_sites.append(site)
        self.enqueued_data.clear()

        enqueued_sites = self._sort_sites_list(enqueued_sites)
        self._save_sites_list(enqueued_sites)
        enqueued_sites.clear()

    def _save_site(self, site: ParsedFeedSite) -> None:
        if not os.path.exists(self._site_path(site)):
            os.mkdir(self._site_path(site))

    def _save_entries(self, entries: List[ParsedFeedItem], site: ParsedFeedSite) -> None:
        entry_template = self._load_template(ENTRY_TEMPLATE)

        for entry in entries:
            entry_filename = os.path.join(self._site_path(site), entry.html_filename)
            with open(entry_filename, "w") as entry_file_handle:
                entry_file_handle.write(
                    entry_template.format(
                        title=entry.title,
                        link=entry.link,
                        back_link="{folder}/index.html".format(folder=site.title_for_filename),
                        published=self._stringified_date(entry.published, include_time=True),
                        content=entry.content,
                    )
                )

    def _save_entries_list(self, entries: List[ParsedFeedItem], site: ParsedFeedSite) -> None:
        entry_list_item_template = self._load_template(ENTRIES_LIST_ITEM_TEMPLATE)

        entries_markup = "\n".join(
            [
                entry_list_item_template.format(
                    relative_path="{folder}/{file}".format(folder=site.title_for_filename, file=entry.html_filename),
                    title=entry.title,
                    published=self._stringified_date(entry.published),
                )
                for entry in entries
            ]
        )

        with open(os.path.join(self._site_path(site), "index.html"), "w") as entries_list_file_handle:
            entries_list_file_handle.write(self._load_template(ENTRIES_LIST_TEMPLATE).format(entries=entries_markup))

    def _sort_sites_list(self, sites: List[ParsedFeedSite]) -> List[ParsedFeedSite]:
        return sorted(sites, key=lambda s: s.title)

    def _save_sites_list(self, sites: List[ParsedFeedSite]) -> None:
        sites_category_template = self._load_template(SITES_CATEGORY_TEMPLATE)
        sites_list_item_template = self._load_template(MAIN_SITES_LIST_ITEM_TEMPLATE)

        sites_by_category = defaultdict(list)
        for site in sites:
            category = site.category if site.category else NO_CATEGORY_TITLE

            sites_by_category[category].append(
                sites_list_item_template.format(
                    relative_path="{folder}/index.html".format(folder=site.title_for_filename),
                    title=site.title,
                    last_update=self._stringified_date(site.last_updated),
                    last_update_ts=self._js_timestamp(site.last_updated),
                )
            )

        sites_markup = ""
        for category in sorted(sites_by_category.keys()):
            category_id = self._category_id_for_html(category)
            if category_id in self.settings.category_icons:
                icon = "{} ".format(self.settings.category_icons[category_id])
            else:
                icon = ""

            sites_markup += sites_category_template.format(
                category=category,
                sites="\n".join(sites_by_category[category]),
                category_id=self._category_id_for_html(category),
                icon=icon,
            )

        with open(os.path.join(self.settings.base_output_path, "index.html"), "w") as sites_list_file_handle:
            sites_list_file_handle.write(self._load_template(MAIN_TEMPLATE).format(sites=sites_markup))

    def _ensure_base_path(self) -> None:
        if not os.path.exists(self.settings.base_output_path):
            os.mkdir(self.settings.base_output_path)

    def _site_path(self, site: ParsedFeedSite) -> str:
        return os.path.join(self.settings.base_output_path, site.title_for_filename)

    @staticmethod
    def _stringified_date(original_date: datetime, include_time: bool = False) -> str:
        if include_time:
            return original_date.strftime("%Y-%m-%d %H:%M")
        else:
            return original_date.strftime("%Y-%m-%d")

    @staticmethod
    def _js_timestamp(original_date: datetime) -> int:
        return int(original_date.timestamp() * 1000)

    @staticmethod
    def _category_id_for_html(category: str) -> str:
        return "id-" + "".join([char for char in category if char.isalnum()])

    @staticmethod
    def _load_template(template_name: str) -> str:
        with open(
            os.path.join(BASE_FOLDER, TEMPLATES_FOLDER, "{name}.html".format(name=template_name))
        ) as template_file_handle:
            return template_file_handle.read()

    # Note that it won't check individual file presence, nor differences in content. If they get updated, just delete
    # and let it re-create corresponding folder with new files
    def _copy_template_required_files_if_needed(self) -> None:
        for folder in ["css", "fonts", "js"]:
            path = os.path.join(self.settings.base_output_path, folder)
            if not os.path.exists(path):
                copy_tree(os.path.join(BASE_FOLDER, TEMPLATES_FOLDER, folder), path)

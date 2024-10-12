import json
import os
import shutil
from datetime import datetime
from typing import List, Tuple

from pbrr.log import Log
from pbrr.parsed_feed_item import ParsedFeedItem
from pbrr.parsed_feed_site import ParsedFeedSite
from pbrr.settings import Settings

BASE_FOLDER = "pbrr"
TEMPLATES_FOLDER = "templates"

NO_CATEGORY_TITLE = "Uncategorized"

SITES_LIST_FILE = "sites.json"
LAST_UPDATED_FILE = "last-updated.json"

KEY_SITES = "sites"
KEY_DATETIME = "date"
KEY_ENTRIES = "entries"
KEY_TITLE = "title"
KEY_URL = "url"
KEY_CONTENT = "content"
KEY_CATEGORY = "category"
KEY_CATEGORY_ICON = "category_icon"

MAIN_TEMPLATE = "index"


class Writer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.enqueued_data: List[Tuple[ParsedFeedSite, List[ParsedFeedItem]]] = []

    def enqueue(self, site: ParsedFeedSite, entries: List[ParsedFeedItem]) -> None:
        self.enqueued_data.append((site, entries))

    def save_data(self) -> None:
        self._ensure_base_path()

        self._copy_template_required_files()

        sites_list = []

        for (
            site,
            entries,
        ) in self.enqueued_data:
            sites_list.append(f"{site.title_for_filename}.json")
            self._save_site_data(site, entries)

        self._save_sites_list(sites_list)

        self._save_last_updated()

    def _save_last_updated(self) -> None:
        data = {
            "timestamp": datetime.now().timestamp(),
        }

        with open(os.path.join(self.settings.base_output_path, LAST_UPDATED_FILE), "w", encoding="utf8") as file_handle:
            json.dump(data, file_handle, indent=2)

    def _save_sites_list(self, sites_list: List[str]) -> None:
        data = {
            KEY_SITES: sites_list,
        }

        with open(os.path.join(self.settings.base_output_path, SITES_LIST_FILE), "w", encoding="utf8") as file_handle:
            json.dump(data, file_handle, indent=2)

    def _save_site_data(self, site: ParsedFeedSite, entries: List[ParsedFeedItem]) -> None:
        site_filepath = self._site_data_path(site)
        data = {
            KEY_TITLE: site.title,
            KEY_CATEGORY: site.category,
            KEY_CATEGORY_ICON: self.settings.category_icons.get(site.category, None),
            KEY_ENTRIES: {
                str(entry.published.timestamp()): {
                    KEY_TITLE: entry.title,
                    KEY_DATETIME: entry.published.timestamp(),
                    KEY_URL: entry.link,
                    KEY_CONTENT: entry.content,
                }
                for entry in entries
            },
        }
        with open(site_filepath, "w", encoding="utf8") as file_handle:
            json.dump(data, file_handle, indent=2)
        Log.info(f"> Written: {site.title} ({len(entries)} entries)")

    def _ensure_base_path(self) -> None:
        if not os.path.exists(self.settings.base_output_path):
            os.mkdir(self.settings.base_output_path)

    def _site_data_path(self, site: ParsedFeedSite) -> str:
        return os.path.join(self.settings.base_output_path, f"{site.title_for_filename}.json")

    def _copy_template_required_files(self) -> None:
        for folder in ["css", "js", "fonts"]:
            path = os.path.join(self.settings.base_output_path, folder)
            shutil.copytree(os.path.join(BASE_FOLDER, TEMPLATES_FOLDER, folder), path, dirs_exist_ok=True)
        for file in ["index.html"]:
            shutil.copy2(
                os.path.join(BASE_FOLDER, TEMPLATES_FOLDER, file), os.path.join(self.settings.base_output_path, file)
            )

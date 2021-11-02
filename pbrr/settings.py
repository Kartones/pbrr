import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from pbrr.log import Log

SETTINGS_FILENAME = "settings-v2.json"
# domains to skip (e.g. can't fetch right now via pbrr). to be manually added editing the settings json
KEY_SKIP_URLS = "skip_urls"
# map of category id -> emoji prefix. to be manually added editing the settings json
KEY_EMOJI_ICONS = "category_emoji_icons"
# list of case-sensitive substrings that, if match at an entry's title, the entry will be skipped
KEY_SKIP_FILTERS = "skip_filters"


class Settings:
    def __init__(self, base_output_path: str) -> None:
        self.base_output_path = base_output_path
        self.last_fetch_mark = None  # type: Optional[datetime]
        self.skip_urls = []  # type: List[str]
        self.category_icons = {}  # type: Dict[str, str]
        self.skip_filters = []  # type: List[str]

    def load(self) -> None:
        file_path = os.path.join(self.base_output_path, SETTINGS_FILENAME)
        if os.path.exists(file_path):
            with open(file_path, "r") as file_handle:
                data = json.load(file_handle)

            self.skip_urls = data[KEY_SKIP_URLS]
            Log.info("> Skip urls list: {}".format(self.skip_urls))

            self.category_icons = data.get(KEY_EMOJI_ICONS, {})

            self.skip_filters = data.get(KEY_SKIP_FILTERS, [])

    def save(self) -> None:
        file_path = os.path.join(self.base_output_path, SETTINGS_FILENAME)

        if not os.path.exists(self.base_output_path):
            Log.error_and_exit("Output path '{}' not found".format(self.base_output_path))

        data = {
            KEY_SKIP_URLS: self.skip_urls,
            KEY_EMOJI_ICONS: self.category_icons,
            KEY_SKIP_FILTERS: self.skip_filters,
        }

        with open(file_path, "w") as file_handle:
            json.dump(data, file_handle, indent=None)

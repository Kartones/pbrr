import json
import os
from typing import Dict, List

from pbrr.log import Log

SETTINGS_FILENAME = "settings-v2.json"
# domains to skip (e.g. can't fetch right now via pbrr). to be manually added editing the settings json
KEY_SKIP_URLS = "skip_urls"
# map of category id -> emoji prefix. to be manually added editing the settings json
KEY_EMOJI_ICONS = "category_emoji_icons"
# list of case-insensitive substrings that, if match at an entry's title, the entry will be skipped
KEY_SKIP_FILTERS = "skip_filters"
# list of case-insensitive substrings that, if match at an entry's content, the entry will be skipped
KEY_SKIP_CONTENT_FILTERS = "skip_content_filters"
# Number of (maximum) entries per feed to keep
KEY_ENTRIES_PER_FEED = "num_entries_per_feed"
# If an entry is older than this number of months, will get filtered out. `None` disables this feature
KEY_ENTRY_MAX_AGE_MONTHS = "entry_max_age_months"


class Settings:
    def __init__(self, base_output_path: str) -> None:
        self.base_output_path = base_output_path
        self.skip_urls: List[str] = []
        self.category_icons: Dict[str, str] = {}
        self.skip_filters: List[str] = []
        self.skip_content_filters: List[str] = []
        self.num_entries_per_feed = 10
        self.entry_max_age_months = None

    def load(self) -> None:
        file_path = os.path.join(self.base_output_path, SETTINGS_FILENAME)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf8") as file_handle:
                data = json.load(file_handle)

            self.skip_urls = data[KEY_SKIP_URLS]
            Log.info(f"> Skip urls list: {self.skip_urls}")
            self.category_icons = data.get(KEY_EMOJI_ICONS, {})
            self.skip_filters = data.get(KEY_SKIP_FILTERS, [])
            self.skip_content_filters = data.get(KEY_SKIP_CONTENT_FILTERS, [])
            self.num_entries_per_feed = data.get(KEY_ENTRIES_PER_FEED, 10)
            self.entry_max_age_months = data.get(KEY_ENTRY_MAX_AGE_MONTHS, None)

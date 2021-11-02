import json
import os
from typing import Dict, List

from pbrr.log import Log

SETTINGS_FILENAME = "settings-v2.json"
# domains to skip (e.g. can't fetch right now via pbrr). to be manually added editing the settings json
KEY_SKIP_URLS = "skip_urls"
# map of category id -> emoji prefix. to be manually added editing the settings json
KEY_EMOJI_ICONS = "category_emoji_icons"
# list of case-sensitive substrings that, if match at an entry's title, the entry will be skipped
KEY_SKIP_FILTERS = "skip_filters"
# Number of (maximum) entries per feed to keep
KEY_ENTRIES_PER_FEED = "num_entries_per_feed"
# If an entry is older than this number of months, will get filtered out. `None` disables this feature
KEY_ENTRY_MAX_AGE_MONTHS = "entry_max_age_months"


class Settings:
    def __init__(self, base_output_path: str) -> None:
        self.base_output_path = base_output_path
        self.skip_urls = []  # type: List[str]
        self.category_icons = {}  # type: Dict[str, str]
        self.skip_filters = []  # type: List[str]
        self.num_entries_per_feed = 10
        self.entry_max_age_months = None

    def load(self) -> None:
        file_path = os.path.join(self.base_output_path, SETTINGS_FILENAME)
        if os.path.exists(file_path):
            with open(file_path, "r") as file_handle:
                data = json.load(file_handle)

            self.skip_urls = data[KEY_SKIP_URLS]
            Log.info("> Skip urls list: {}".format(self.skip_urls))
            self.category_icons = data.get(KEY_EMOJI_ICONS, {})
            self.skip_filters = data.get(KEY_SKIP_FILTERS, [])
            self.num_entries_per_feed = data.get(KEY_ENTRIES_PER_FEED, 10)
            self.entry_max_age_months = data.get(KEY_ENTRY_MAX_AGE_MONTHS, None)

    def save(self) -> None:
        file_path = os.path.join(self.base_output_path, SETTINGS_FILENAME)

        if not os.path.exists(self.base_output_path):
            Log.error_and_exit("Output path '{}' not found".format(self.base_output_path))

        data = {
            KEY_SKIP_URLS: self.skip_urls,
            KEY_EMOJI_ICONS: self.category_icons,
            KEY_SKIP_FILTERS: self.skip_filters,
            KEY_ENTRIES_PER_FEED: self.num_entries_per_feed,
            KEY_ENTRY_MAX_AGE_MONTHS: self.entry_max_age_months,
        }

        with open(file_path, "w") as file_handle:
            json.dump(data, file_handle, indent=None)

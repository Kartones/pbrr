import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from pbrr.log import Log

SETTINGS_FILENAME = "settings.json"
KEY_LAST_FETCH = "last_fetch"
# domains to skip (e.g. can't fetch right now via pbrr). to be manually added editing the settings json
KEY_SKIP_URLS = "skip_urls"
# map of category id -> emoji prefix. to be manually added editing the settings json
KEY_EMOJI_ICONS = "category_emoji_icons"


class Settings:
    def __init__(self, base_output_path: str) -> None:
        self.base_output_path = base_output_path
        self.last_fetch_mark = None  # type: Optional[datetime]
        self.skip_urls = []  # type: List[str]
        self.category_icons = {}  # type: Dict[str, str]

    def load(self) -> None:
        file_path = os.path.join(self.base_output_path, SETTINGS_FILENAME)
        if os.path.exists(file_path):
            with open(file_path, "r") as file_handle:
                data = json.load(file_handle)

            last_fetch = data.get(KEY_LAST_FETCH, None)
            if last_fetch:
                self.last_fetch_mark = datetime.utcfromtimestamp(last_fetch)
                Log.info("> Previous fetch mark was: {}".format(self.last_fetch_mark))

            self.skip_urls = data[KEY_SKIP_URLS]
            Log.info("> Skip urls list: {}".format(self.skip_urls))

            self.category_icons = data.get(KEY_EMOJI_ICONS, {})

    def save(self) -> None:
        fetch_mark = datetime.now()
        file_path = os.path.join(self.base_output_path, SETTINGS_FILENAME)

        if not os.path.exists(self.base_output_path):
            Log.error_and_exit("Output path '{}' not found".format(self.base_output_path))

        data = {
            KEY_LAST_FETCH: fetch_mark.timestamp(),
            KEY_SKIP_URLS: self.skip_urls,
            KEY_EMOJI_ICONS: self.category_icons,
        }

        with open(file_path, "w") as file_handle:
            json.dump(data, file_handle, indent=None)

        Log.info("> Fetch mark set to: {}".format(fetch_mark))

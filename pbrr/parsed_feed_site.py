import re
import time
from typing import Optional


class ParsedFeedSite:

    # .isalnum() leaves accents and other unwanted characters
    REGEX_ONLY_ALPHANUMERIC = re.compile("[^a-zA-Z]")

    # When parsing actual feeds `last_updated` should never be none (at minimum, epoch), but when receiving 304s we do
    # set None as we don't know the last update time
    def __init__(
        self, title: str, category: Optional[str], link: str, last_updated: Optional[time.struct_time]
    ) -> None:
        self.title = title
        self.link = link
        self.category = category
        self.last_updated = last_updated if last_updated else time.gmtime(0)

    def __str__(self) -> str:
        return "ParsedFeedSite: {title} - {category} ({link}) last update: {last_updated}".format(
            title=self.title, category=self.category, link=self.link, last_updated=self.last_updated
        )

    @property
    def title_for_filename(self) -> str:
        return self.REGEX_ONLY_ALPHANUMERIC.sub("", self.title.lower())

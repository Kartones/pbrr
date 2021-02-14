import re
import time


class ParsedFeedSite:

    # .isalnum() leaves accents and other unwanted characters
    REGEX_ONLY_ALPHANUMERIC = re.compile("[^a-zA-Z]")

    def __init__(self, title: str, link: str, last_updated: time.struct_time) -> None:
        self.title = title
        self.link = link
        self.last_updated = last_updated

    def __str__(self) -> str:
        return "ParsedFeedSite: {title} ({link}) last update: {last_updated}".format(
            title=self.title, link=self.link, last_updated=self.last_updated
        )

    @property
    def title_for_filename(self) -> str:
        return self.REGEX_ONLY_ALPHANUMERIC.sub("", self.title.lower())

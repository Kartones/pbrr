import hashlib
from datetime import datetime
from typing import Optional


class ParsedFeedSite:
    def __init__(self, title: str, category: Optional[str], link: str, last_updated: Optional[datetime]) -> None:
        self.title = title
        self.link = link
        self.category = category
        if last_updated and last_updated.year > 1900:
            self.last_updated = last_updated
        else:
            self.last_updated = datetime.fromisoformat("1970-01-01")

    def __str__(self) -> str:
        return "ParsedFeedSite: {title} - {category} ({link}) last update: {last_updated}".format(
            title=self.title, category=self.category, link=self.link, last_updated=self.last_updated
        )

    @property
    def id(self) -> str:
        hashAlgoritm = hashlib.md5()
        hashAlgoritm.update(str.encode(self.link if self.link else self.title))
        return hashAlgoritm.hexdigest()

    @property
    def title_for_filename(self) -> str:
        return self.id

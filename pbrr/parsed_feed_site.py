import hashlib
from typing import Optional


class ParsedFeedSite:
    def __init__(self, title: str, category: Optional[str], link: str) -> None:
        self.title = title
        self.link = link
        self.category = category

    def __str__(self) -> str:
        return "ParsedFeedSite: {title} - {category} ({link})".format(
            title=self.title, category=self.category, link=self.link
        )

    @property
    def id(self) -> str:
        hashAlgoritm = hashlib.md5()
        hashAlgoritm.update(str.encode(self.title))
        return hashAlgoritm.hexdigest()

    @property
    def title_for_filename(self) -> str:
        return self.id

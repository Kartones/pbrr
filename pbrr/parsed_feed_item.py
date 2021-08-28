import hashlib
from datetime import datetime

from pbrr.parsed_feed_site import ParsedFeedSite


class ParsedFeedItem:
    def __init__(self, title: str, link: str, published: datetime, content: str, parent: ParsedFeedSite) -> None:
        self.title = title
        self.link = link
        self.published = published
        self.content = content
        self.parent = parent

    def __str__(self) -> str:
        return "ParsedFeedItem: {title} ({link}) parent:{parent} published: {published} len(content): {content_length}".format(  # NOQA: E501
            title=self.title,
            link=self.link,
            parent=self.parent.title,
            published=self.published,
            content_length=len(self.content),
        )

    @property
    def id(self) -> str:
        hashAlgoritm = hashlib.md5()
        # Because some feeds contain non-unique links (e.g. Github activity RSS points to repositories)
        hashAlgoritm.update(str.encode(self.link + self.title))
        return hashAlgoritm.hexdigest()

    @property
    def html_filename(self) -> str:
        return "{ts}_{id}.html".format(ts=self.date_for_filename, id=self.id)

    @property
    def date_for_filename(self) -> str:
        return "{ts}".format(ts=int(self.published.timestamp()))

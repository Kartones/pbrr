import time
from typing import Optional

from pbrr.parsed_feed_site import ParsedFeedSite


class ParsedFeedItem:
    def __init__(
        self, title: str, link: str, published: Optional[time.struct_time], content: str, parent: ParsedFeedSite
    ) -> None:
        self.title = title
        self.link = link
        self.published = published if published else time.gmtime(0)
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
    def html_filename(self) -> str:
        return "{}.html".format(self.date_for_filename)

    @property
    def date_for_filename(self) -> str:
        return "{ts}".format(ts=time.mktime(self.published))

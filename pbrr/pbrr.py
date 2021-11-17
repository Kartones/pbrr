from typing import List, cast

from pbrr.parsed_feed_item import ParsedFeedItem
from pbrr.parsed_feed_site import ParsedFeedSite
from pbrr.parser import Parser
from pbrr.settings import Settings
from pbrr.writer import Writer


class PBRR:
    def __init__(self, data_path: str, opml_filename: str) -> None:
        self.data_path = data_path
        self.opml_filename = opml_filename

    def run(self) -> None:
        settings = Settings(base_output_path=self.data_path)
        settings.load()

        parser = Parser(settings=settings)
        writer = Writer(settings=settings)

        sites_metadata = parser.fetch_sites_metadata(self.opml_filename)

        for url, title, category in sites_metadata:
            try:
                parsed_data = parser.fetch_site(url=url, title=title, category=category)
            except ValueError:
                continue

            site = cast(ParsedFeedSite, parsed_data[Parser.KEY_SITE])
            entries = cast(List[ParsedFeedItem], parsed_data[Parser.KEY_ENTRIES])

            writer.enqueue(site, entries)

        writer.save_data()
        settings.save()


from typing import Any
import feedparser
from chat_with_rss.page_reader import PageReader
import logging

log = logging.getLogger(__name__)

class RssReader:


    def __init__(self, url: str):
        self.url = url


    def _get_feed(self) -> feedparser.FeedParserDict:
        feed = feedparser.parse(self.url)
        return feed
    

    def parse_feed(self, limit: int = 1000) -> list[dict[str, Any]]:
        """parse the feed and return a list of entries

        :param limit: limit the number of entries to return, defaults to 1000
        :return: list of feed entries as dicts
        """        
        feed = self._get_feed()
        feed.entries = feed.entries[:limit] # type: ignore
        log.info(f"Found {len(feed.entries)} entries in the feed.")
        entries = []
        for entry in feed.entries:
            entries.append(dict(entry))
        return entries



import feedparser
from chatwithrss.page_reader import PageReader


class RssReader:


    def __init__(self, url: str):
        self.url = url


    def _get_feed(self) -> feedparser.FeedParserDict:
        feed = feedparser.parse(self.url)
        return feed
    

    def parse_feed(self, limit: int = 1000, append_content: bool = False) -> list[feedparser.FeedParserDict]:
        feed = self._get_feed()
        feed.entries = feed.entries[:limit] # type: ignore
        if append_content:
            # append the page content to the feed entries
            pages_content = PageReader.read([str(entry.link) for entry in feed.entries])
            for entry, page_content in zip(feed.entries, pages_content):
                entry['page_content'] = page_content['page_content']
        return feed.entries


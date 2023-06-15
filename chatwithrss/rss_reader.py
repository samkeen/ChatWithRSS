
import feedparser



class RssReader:


    def __init__(self, url: str):
        self.url = url


    def _get_feed(self) -> feedparser.FeedParserDict:
        feed = feedparser.parse(self.url)
        return feed
    

    def parse_feed(self) -> list[feedparser.FeedParserDict]:
        feed = self._get_feed()
        return feed.entries

    
if __name__ == "__main__":
    from page_reader import PageReader
    reader = RssReader("https://aws.amazon.com/about-aws/whats-new/recent/feed/")
    feed_entries = reader.parse_feed()
    
    links = [str(entry.link) for entry in feed_entries]
    page_content = PageReader.read(links)
    # create a file
    with open("rss_content.txt", "w") as f:
        f.write("```\n")
        for doc in page_content:
            f.write(doc)
            f.write("\n```")
            f.write("\n")

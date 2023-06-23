from chat_with_rss.rss_reader import RssReader
from dotenv import load_dotenv
from chat_with_rss.feed_persister import FeedPersister
from pathlib import Path
# read ENV variables
load_dotenv()

# set logging level
import logging
# Set global logging to ERROR, then set the logging level for chatwithrss to DEBUG
logging.basicConfig(level=logging.ERROR)
logging.getLogger("chat_with_rss").setLevel(logging.DEBUG)


# Get all the entries in the RSS feed
rss_reader = RssReader("https://aws.amazon.com/about-aws/whats-new/recent/feed/")
feed_entries = rss_reader.parse_feed(limit=1000)

# Ingest each entry into the vector store
docs_db = FeedPersister(Path().joinpath(".chromadb"), metadata_fields=["link", "id", "published"])
docs_db.ingest(feed_entries)

import os
from chat_with_rss.rss_reader import RssReader
from dotenv import load_dotenv
from chat_with_rss.feed_persister import FeedPersister
from pathlib import Path
# read ENV variables
load_dotenv()

FEED_URL = os.getenv("FEED_URL")
FEED_ITEMS_LIMIT = os.getenv("FEED_ITEMS_LIMIT")
if not FEED_URL:
    exit("No FEED_URL provided in .env file")
if not FEED_ITEMS_LIMIT:
    exit("No FEED_ITEMS_LIMIT provided in .env file, using 50 as default")

# set logging level
import logging
# Set global logging to ERROR, then set the logging level for chatwithrss to DEBUG
logging.basicConfig(level=logging.ERROR)
logging.getLogger("chat_with_rss").setLevel(logging.DEBUG)


# Get all the entries in the RSS feed
rss_reader = RssReader(FEED_URL)
feed_entries = rss_reader.parse_feed(limit=int(FEED_ITEMS_LIMIT))

# Ingest each entry into the vector store
docs_db = FeedPersister(Path().joinpath(".chromadb"), metadata_fields=["link", "id", "published"])
docs_db.ingest(feed_entries)

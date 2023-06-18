from chatwithrss.rss_reader import RssReader
from dotenv import load_dotenv
from chatwithrss.docs_db import DocsDb
# read ENV variables
load_dotenv()

# set logging level
import logging
logging.basicConfig(level=logging.INFO)
# set logging level to debug only for chatwithrss
logging.getLogger("chatwithrss").setLevel(logging.DEBUG)


# Get all the entries in the RSS feed
rss_reader = RssReader("https://aws.amazon.com/about-aws/whats-new/recent/feed/")
feed_entries = rss_reader.parse_feed(append_content=True, limit=20)

# pretty print the first entry
import pprint  
pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(feed_entries[0])

# Ingest each entry into the vector store

docs_db = DocsDb(metadata_fields=["link", "id"])
docs_db.ingest(feed_entries)

search_results = docs_db.search("lambda")

# pretty print the search results
pp.pprint(search_results)
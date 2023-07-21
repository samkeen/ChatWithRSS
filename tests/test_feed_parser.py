# Tests that ingesting a list of rss documents with valid metadata fields adds the documents to the vector datastore
from pathlib import Path
import tempfile
from chat_with_rss.feed_persister import FeedPersister


def test_ingest_valid_metadata_fields():
    # create a temporary directory for the vector store
    with tempfile.TemporaryDirectory() as tmp_dir:
        # create a FeedPersister instance
        feed_persister = FeedPersister(
            persist_dir_path=Path(tmp_dir),
            metadata_fields=['id', 'title', 'link']
        )
        # create some rss documents with valid metadata fields
        rss_documents = [
            {
                'id': '1',
                'title': 'Test Document 1',
                'link': 'https://example.com/document1'
            },
            {
                'id': '2',
                'title': 'Test Document 2',
                'link': 'https://example.com/document2'
            }
        ]
        # ingest the rss documents
        feed_persister.ingest(rss_documents)
        # get all documents from the vector store
        results = feed_persister.get_all_documents()
        # check that the number of documents in the vector store is correct
        assert len(results['documents']) == len(rss_documents)
        # check that each document in the vector store has the correct metadata fields
        for result in results['metadatas']:
            assert result['id'] in [doc['id'] for doc in rss_documents]
            assert result['title'] in [doc['title'] for doc in rss_documents]
            assert result['link'] in [doc['link'] for doc in rss_documents]


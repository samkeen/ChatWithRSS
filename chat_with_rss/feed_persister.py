from datetime import datetime
from typing import Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from pathlib import Path
import logging
import json
from pathlib import Path

from chat_with_rss.page_reader import PageReader


log = logging.getLogger(__name__)


class FeedPersister:
    """
    Class for ingesting documents into a vector datastore
    We are using the Chroma vector store
    see: https://python.langchain.com/docs/modules/data_connection/vectorstores/integrations/chroma
    """

    def __init__(
        self,
        persist_dir_path: Path,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        metadata_fields: list = [],
    ):
        # https://python.langchain.com/en/latest/modules/indexes/text_splitters/getting_started.html
        # The default recommended text splitter is the RecursiveCharacterTextSplitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        # the fields of the document that will be used as metadata
        self.metadata_fields = metadata_fields
        # intanciate the OpenAI embeddings model
        self.embeddings = OpenAIEmbeddings()  # type: ignore
        self.persist_dir_path = persist_dir_path
        self.db = None

    def get_all_documents(self) -> dict[str, Any]:
        """Returns all documents in the datastore"""
        db = Chroma(
            persist_directory=str(self.persist_dir_path.absolute()),
            embedding_function=self.embeddings,
        )
        results = db.get()
        db = None
        return results

    def ingest(self, rss_documents: list[dict[str, str]]) -> None:
        db_documents = []  # type: list[Document]
        if not rss_documents:
            log.info(f"RSS documents list is empty. Nothing to ingest.")
            return
        items_to_persist = []
        existing_persisted_items = self._load_persisted_ids()
        existing_ids = [item["id"] for item in existing_persisted_items]
        # build the metadata for each document
        self._contruct_metadata(rss_documents, db_documents, items_to_persist, existing_ids)
        # ingest the documents into the datastore
        if db_documents:
            self._add_page_content(db_documents)
            self._persist_to_vector_db(
                rss_documents, db_documents, items_to_persist, existing_persisted_items
            )


    def _persist_to_vector_db(
        self, rss_documents, db_documents, items_to_persist, existing_persisted_items
    ):
        vector_db = Chroma.from_documents(
            db_documents,
            self.embeddings,
            ids=[item["id"] for item in items_to_persist],
            persist_directory=str(self.persist_dir_path.absolute()),
        )
        log.info(f"Ingested {len(rss_documents)} documents")
        vector_db.persist()
        existing_persisted_items.extend(items_to_persist)
        log.info(f"Total persisted items coumnt: {len(existing_persisted_items)}")
        self._write_persisted_ids(existing_persisted_items)

    def _add_page_content(self, db_documents: list[Document]) -> None:
        pages_content = PageReader.read([doc.metadata.get("link") for doc in db_documents])
        for db_document, page_content in zip(db_documents, pages_content):
            db_document.page_content = page_content["page_content"]

    def _contruct_metadata(self, rss_documents, db_documents, items_to_persist, existing_ids):
        for rss_document in rss_documents:
            # Build the metadata dictionary
            metadata = {
                field: rss_document[field]
                for field in self.metadata_fields
                if field in rss_document
            }
            if metadata.get("id") in existing_ids:
                log.debug(
                    f"Skipping document with id {metadata.get('id')} because it already exists"
                )
                continue
            items_to_persist.append(metadata)
            # Start the document with an empty page_content (added later)
            document = Document(page_content="", metadata=metadata)
            log.debug(f"Created Document for injest: {document}")
            db_documents.append(document)

    def search(self, query: str) -> list[dict[str, Any]]:
        """Searches the vector datastore for a given query"""
        if self.db is None:
            raise Exception("You must ingest documents before searching")
        # query_chunks = self.text_splitter.split_text(query)
        # query_documents = [Document(page_content=chunk) for chunk in query_chunks]
        results = self.db.similarity_search(query)
        return self._format_search_results(results)

    def _format_search_results(self, results: list[Document]) -> list[dict[str, Any]]:
        """restructure the resultes to a more usable format

        :param results: List of Document objects
        :return: List of dictionaries
        """
        dict_results = []
        for result in results:
            result_item = {
                "page_content": result.page_content,
            }
            for field in self.metadata_fields:
                result_item[field] = result.metadata.get(field, "")
            dict_results.append(result_item)
        return dict_results

    def _load_persisted_ids(self) -> list[dict[str, Any]]:
        """
        Get the list of ids that have been persisted to the vector store.
        This is so we can filter out documents that have already been indexed when ingesting new documents.
        """
        filename = self.persist_dir_path.joinpath("persisted_items.json")
        data = []
        if filename.exists():
            with filename.open("r") as f:
                data = json.load(f)
        else:
            print(f"{filename} does not exist")
        return data

    def _write_persisted_ids(self, ids: list[dict[str, str]]) -> None:
        """
        This is a bit of a hack, write the ids to a file that have been indexed in the vector store.
        This is so we can filter out documents that have already been indexed when ingesting new documents.
        """
        filename = self.persist_dir_path.joinpath("persisted_items.json")
        with filename.open("w") as f:
            json.dump(ids, f)

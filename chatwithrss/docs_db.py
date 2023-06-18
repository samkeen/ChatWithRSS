from typing import Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from pathlib import Path
import logging


log = logging.getLogger(__name__)

class DocsDb:
    """
    Class for ingesting documents into a vector datastore
    We are using the Chroma vector store
    see: https://python.langchain.com/docs/modules/data_connection/vectorstores/integrations/chroma
    """


    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100, metadata_fields: list = []):
        # https://python.langchain.com/en/latest/modules/indexes/text_splitters/getting_started.html
        # The default recommended text splitter is the RecursiveCharacterTextSplitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        # the fields of the document that will be used as metadata
        self.metadata_fields = metadata_fields
        # intanciate the OpenAI embeddings model
        self.embeddings = OpenAIEmbeddings() # type: ignore
        self.db_perist_dir = Path().parent.absolute().joinpath(".chromadb")
        log.debug(f"Using {self.db_perist_dir} as the vector store directory")
        self.db = None


    def ingest(self, documents: list[dict[str,str]]) -> None:
        db_documents = []
        if documents:
            log.debug(f"Ingesting {len(documents)} documents")
        for document in documents:
            # Build the metadata dictionary
            metadata = {field: document[field] for field in self.metadata_fields if field in document}
            db_documents.append(Document(
                page_content=document["page_content"],
                metadata=metadata
            ))
            
        self.db = Chroma.from_documents(db_documents, self.embeddings, persist_directory=str(self.db_perist_dir))


    def search(self, query: str) -> list[dict[str, Any]]:
        """Searches the vector datastore for a given query"""
        if self.db is None:
            raise Exception("You must ingest documents before searching")
        # query_chunks = self.text_splitter.split_text(query)
        # query_documents = [Document(page_content=chunk) for chunk in query_chunks]
        results = self.db.similarity_search(query)
        return self._format_search_results(results)
        
    
    def _format_search_results(self, results: list[Document]) -> list[dict[str, Any]]:
        """
        Formats the search results into a list of dictionaries.

        Args:
            results: The list of search results.

        Returns:
            The list of search results in dictionary format.
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
    
    

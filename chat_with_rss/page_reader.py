
from langchain.document_loaders import SeleniumURLLoader
import logging

logger = logging.getLogger(__name__)

class PageReader:

    @staticmethod
    def read(urls: list[str]) -> list[dict[str, str]]:
        """Get the page content for a list of urls

        :param urls: list of urls to read
        :return: dict with page content and page link
        """
        loader = SeleniumURLLoader(urls=urls)
        logger.info(f"Reading content for {len(urls)} pages...")
        documents = loader.load()
        return [{"page_content": document.page_content, "page_link":document.metadata['source']} for document in documents]


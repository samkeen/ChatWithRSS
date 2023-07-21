from langchain.document_loaders import SeleniumURLLoader
import logging

logger = logging.getLogger(__name__)

class PageReader:
    """The PageReader class is responsible for reading the content of a list of URLs and returning a list of dictionaries 
    containing the page content and link for each URL. It uses the SeleniumURLLoader class to load the web pages and 
    extract their content.
    """

    @classmethod
    def read(cls, urls: list[str]) -> list[dict[str, str]]:
        """Get the page content for a list of urls

        :param urls: list of urls to read
        :return: dict with page content and page link
        """
        try:
            cls._validate_url_forms(urls)
            page_content = []
            loader = SeleniumURLLoader(urls=urls)
            logger.info(f"Reading content for {len(urls)} pages...")
            documents = loader.load()
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return []
        else:
            return [{"page_content": document.page_content, "page_link":document.metadata['source']} for document in documents]

    @classmethod
    def _validate_url_forms(cls, urls: list[str]):
        if not isinstance(urls, list):
                raise ValueError("urls must be a list")
        valid_urls = [url for url in urls if isinstance(url, str)]
        if not valid_urls:
            raise ValueError("Each url must be a string")
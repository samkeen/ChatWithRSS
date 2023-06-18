
from selenium import webdriver
from langchain.document_loaders import SeleniumURLLoader
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

class PageReader:

    @staticmethod
    def read(urls: list[str]) -> list[dict[str, str]]:
        loader = SeleniumURLLoader(urls=urls)
        documents = loader.load()
        return [{"page_content": document.page_content, "page_link":document.metadata['source']} for document in documents]



if __name__ == "__main__":
    reader = PageReader()

    page_content = reader.read([
        "https://aws.amazon.com/about-aws/whats-new/2023/06/aws-lambda-snapstart-java-7-additional-regions",
        "https://aws.amazon.com/about-aws/whats-new/2023/06/single-region-terraform-control-tower-account-factory/"
        ])
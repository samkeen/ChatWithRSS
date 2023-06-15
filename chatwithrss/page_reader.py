
from selenium import webdriver
from langchain.document_loaders import SeleniumURLLoader
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

class PageReader:

    @staticmethod
    def read(urls: list[str]) -> list[str]:
        loader = SeleniumURLLoader(urls=urls)
        documents = loader.load()
        return [document.page_content for document in documents]



if __name__ == "__main__":
    reader = PageReader()
    page_content = reader.read([
        "https://aws.amazon.com/about-aws/whats-new/2023/06/aws-lambda-snapstart-java-7-additional-regions/",
        "https://aws.amazon.com/about-aws/whats-new/2023/06/single-region-terraform-control-tower-account-factory/"
        ])
    logger.info("Got {} documents".format(len(page_content)))
    for doc in page_content:
        print(doc.page_content)
    
import os
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
env_loaded = load_dotenv()
api_key_added = os.getenv("OPENAI_API_KEY", "").strip() != ""
CHROMA_K_VALUE = int(os.getenv("CHROMA_K_VALUE", 4))

def main():
  if not env_loaded or not api_key_added:
    st.error("No .env file found and/or OPENAI_API_KEY not added")
    st.markdown("`cp dist.env .env` Then add your OpenAI API key to the .env file")
    return
  
  if "doc_search" not in st.session_state:
      load_db()

  # show user input
  user_question = st.text_input("Ask a question about new releases from AWS")
  if user_question:
    seven_days_ago = days_ago_epoch(7)
    st.write(seven_days_ago)
    docs = st.session_state.doc_search.get(
      where={"published_epoch": {"$gte": seven_days_ago}},
    )
    st.write(docs)
    # TODO we now have a list of all docs from the last week,
    #  - Get a 500 word summary of all the docs
    llm = OpenAI() # type: ignore
    chain = load_qa_chain(llm, chain_type="stuff")
    with get_openai_callback() as cb:
      response = chain.run(input_documents=docs, question=user_question)
      print(cb)
        
    st.write(response)

def load_db():
  # Create a Chroma vector store
  embeddings = OpenAIEmbeddings() # type: ignore
  st.session_state.doc_search = Chroma(
    persist_directory=str(Path().joinpath(".chromadb").absolute()), 
    embedding_function=embeddings)._collection
  
def days_ago_epoch(days_ago: int) -> int:
  return int((datetime.now() - timedelta(days=days_ago)).timestamp())

# Run the main function
if __name__ == "__main__":
  main()
import os
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from pathlib import Path

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
env_loaded = load_dotenv()
api_key_added = os.getenv("OPENAI_API_KEY", "").strip() != ""
CHROMA_K_VALUE = int(os.getenv("CHROMA_K_VALUE", 4))
OPENAI_MODEL = os.getenv("OPENAI_MODEL")


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
    docs = st.session_state.doc_search.similarity_search(user_question, k=CHROMA_K_VALUE)
    
    llm=ChatOpenAI(
          temperature=0,
          model=OPENAI_MODEL, 
      ) # type: ignore


    template = "respond as succinctly as possible. {query}?"

    prompt = PromptTemplate(
        input_variables=["query"],
        template=template,
    )


    chain = load_qa_chain(llm, chain_type="stuff")
    with get_openai_callback() as cb:
      response = chain.run(input_documents=docs, question=prompt.format(query=user_question))
      print(cb)
        
    st.write(response)


def load_db():
  # Create a Chroma vector store
  embeddings = OpenAIEmbeddings() # type: ignore
  st.session_state.doc_search = Chroma(
    persist_directory=str(Path().joinpath(".chromadb").absolute()), 
    embedding_function=embeddings)
  

# Run the main function
if __name__ == "__main__":
  main()
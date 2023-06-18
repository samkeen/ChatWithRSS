import os
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from PyPDF2 import PdfReader
from dotenv import load_dotenv

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
env_loaded = load_dotenv()
api_key_added = os.getenv("OPENAI_API_KEY").strip() != ""

def main():
  if not env_loaded or not api_key_added:
    st.error("No .env file found and/or OPENAI_API_KEY not added")
    st.markdown("`cp dist.env .env` Then add your OpenAI API key to the .env file")
    return
  
  file = st.file_uploader("Upload your file", type=["pdf", "txt"])
  # Upload the file
  if file is not None:
    
    if "doc_search" not in st.session_state:
      process_file(file)

    # show user input
    user_question = st.text_input("Ask a question about your PDF:")
    if user_question:
      docs = st.session_state.doc_search.similarity_search(user_question)
      
      llm = OpenAI()
      chain = load_qa_chain(llm, chain_type="stuff")
      with get_openai_callback() as cb:
        response = chain.run(input_documents=docs, question=user_question)
        print(cb)
          
      st.write(response)

  # If the user has not uploaded a file, then display an error message
  else:
    st.error("Please upload a file")


def get_pdf_text(pdf):
  pdf_reader = PdfReader(pdf)
  text = ""
  for page in pdf_reader.pages:
    text += page.extract_text()
  return text

def process_file(file):
  # If the user has uploaded a file, then proceed
  document_text = ""
  if file is not None:
    # check the file type
    if file.type == "application/pdf":
      document_text = get_pdf_text(file)
    else:
      document_text = file.read().decode("utf-8")
    # @TODO write document text to a file

  
  chunks = text_splitter.split_text(document_text)

  # Create a metadata for each chunk
  metadatas = [{"source": f"{i}-pl"} for i in range(len(chunks))]

  # Create a Chroma vector store
  embeddings = OpenAIEmbeddings()




  st.session_state.doc_search = Chroma.from_texts(chunks, embeddings, metadatas=metadatas)
  

# Run the main function
if __name__ == "__main__":
  main()
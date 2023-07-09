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
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.0))


def main():
  # Check that there is an OPENAI API key loaded
  if not env_loaded or not api_key_added:
    st.error("No .env file found and/or OPENAI_API_KEY not added")
    st.markdown("`cp dist.env .env` Then add your OpenAI API key to the .env file")
    return
  

  # Load the vector db store is not loaded, place it in session memory
  if "doc_search" not in st.session_state:
      load_db()


  # Prompt the user for their question
  user_question = st.text_input("Ask a question of this RSS feed")


  if user_question:

    # Have Chroma do a similarity search with the uses's supplied query
    # This returns 'k' number of similar documents.
    docs = st.session_state.doc_search.similarity_search(user_question, k=CHROMA_K_VALUE)
    

    # Instantiate an OpenAI LLM
    llm=ChatOpenAI(
          temperature=OPENAI_TEMPERATURE,
          model=OPENAI_MODEL, 
      ) # type: ignore


    # Form the prompt template we will send to the LLM 
    template = "respond as succinctly as possible. {query}?"
    prompt = PromptTemplate(
        input_variables=["query"],
        template=template,
    )


    # Instantiate a Question/Answer Langchain chain.
    # The 'stuff' chain type is the simplest method, whereby you simply stuff all the 
    #   related data into the prompt as context to pass to the language model.
    chain = load_qa_chain(llm, chain_type="stuff")


    # Run the chain and collect the response.
    # Use 'with' context to track token usage
    #   see: https://python.langchain.com/docs/modules/model_io/models/llms/how_to/token_usage_tracking
    with get_openai_callback() as cb:
      response = chain.run(input_documents=docs, question=prompt.format(query=user_question))
      print(cb)
        

    # Display the result to the user    
    st.write(response)


# Load the vector data store into session memory
def load_db():
  # Create a Chroma vector store
  embeddings = OpenAIEmbeddings() # type: ignore
  st.session_state.doc_search = Chroma(
    persist_directory=str(Path().joinpath(".chromadb").absolute()), 
    embedding_function=embeddings)
  

# Run the main function
if __name__ == "__main__":
  main()
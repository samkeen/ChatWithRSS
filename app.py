import os
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
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
    # Borrowed this from
    # .venv/lib/python3.9/site-packages/langchain/chains/question_answering/stuff_prompt.py
    system_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Question: {question}
    Helpful Answer:"""
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
    chat_prompt = ChatPromptTemplate.from_messages(messages)


    # Instantiate a Question/Answer Langchain chain.
    # The 'stuff' chain type is the simplest method, whereby you simply stuff all the 
    #   related data into the prompt as context to pass to the language model.
    chain = load_qa_chain(llm, chain_type="stuff", verbose=True, prompt=chat_prompt)
    prompt_token_length = chain.prompt_length(docs, question=user_question)
    # TODO for now just stop, fix is being worked on here: https://github.com/DevThinkAI/ChatWithRSS/issues/2
    if prompt_token_length and prompt_token_length > 16000:
      st.error(f"Prompt token length is too long: {prompt_token_length} for this model.")
      return


    # Run the chain and collect the response.
    # Use 'with' context to track token usage
    #   see: https://python.langchain.com/docs/modules/model_io/models/llms/how_to/token_usage_tracking
    with get_openai_callback() as cb:
      response = chain.run(input_documents=docs, question=user_question, return_only_outputs=False, include_outputs=True)


    # output some metadata
    st.markdown(f"Found {len(docs)} similar documents in vector store.\n\nUsing OpenAI model: {OPENAI_MODEL}, with temperature: {OPENAI_TEMPERATURE}\n\nPrompt token length: {prompt_token_length}") 
    st.code(f"{cb}")


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
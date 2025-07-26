# app/rag_engine.py

import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.schema import Document

# --- Mode Toggle ---
IS_PRODUCTION = True  # 🔁 Set to False for local development

if IS_PRODUCTION:
    import streamlit as st
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
else:
    load_dotenv("GPT35.env")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Ensure OpenAI SDK sees the key
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# --- Vectorstore index configuration ---
INDEX_DIR = "embeddings"
INDEX_MAP = {
    "Australian Slang": "slang_index",
    "Excel Budgeting": "excel_index",
    "Periodic Table": "periodic_index",
    "MySQL Workshop": "mysql_index",
    "All Topics": "combined_index"
}

# --- Initialize LLM and Embeddings ---
llm = ChatOpenAI(temperature=0.3, openai_api_key=OPENAI_API_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# --- Main response handler ---
def get_response(user_input, system_prompt, book_option, pg_mode=True):
    # Select appropriate FAISS index
    index_name = INDEX_MAP.get(book_option, "combined_index")
    index_path = os.path.join(INDEX_DIR, index_name)

    # Load vectorstore and retriever
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever()

    # Retrieve relevant documents
    docs = retriever.get_relevant_documents(user_input)

    # Optional PG filter
    if pg_mode:
        docs = [doc for doc in docs if doc.metadata.get("pg_safe", True)]

    # If no results
    if not docs:
        return "Crikey, I couldn't find a PG-rated answer for that one. Wanna rephrase it, mate?"

    # Compile context
    context = "\n\n".join(doc.page_content for doc in docs)

    # Construct final prompt
    prompt = f"{system_prompt}\n\n{context}\n\nUser: {user_input}\nAssistant:"

    # Get response from LLM
    response = llm.predict(prompt)

    return response

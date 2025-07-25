# app/rag_engine.py

import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.schema import Document

from dotenv import load_dotenv
load_dotenv("GPT35.env")

# --- Load vectorstore index ---
INDEX_DIR = "embeddings"
INDEX_MAP = {
    "Australian Slang": "slang_index",
    "Excel Budgeting": "excel_index",
    "Periodic Table": "periodic_index",
    "MySQL Workshop": "mysql_index",
    "All Topics": "combined_index"
}

# --- Init LLM ---
llm = ChatOpenAI(temperature=0.3, openai_api_key=os.getenv("OPENAI_API_KEY"))

# --- Get response function ---
def get_response(user_input, system_prompt, book_option, pg_mode=True):
    # Get index path
    index_name = INDEX_MAP.get(book_option, "combined_index")
    index_path = os.path.join(INDEX_DIR, index_name)

    # Load FAISS index
    vectorstore = FAISS.load_local(index_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever()

    # Retrieve top-k documents
    docs = retriever.get_relevant_documents(user_input)

    # Filter if PG mode enabled
    if pg_mode:
        docs = [doc for doc in docs if doc.metadata.get("pg_safe", True)]

    # Handle no results
    if not docs:
        return "Crikey, I couldn't find a PG-rated answer for that one. Wanna rephrase it, mate?"

    # Build context
    context = "\n\n".join(doc.page_content for doc in docs)

    # Build prompt
    prompt = f"{system_prompt}\n\n{context}\n\nUser: {user_input}\nAssistant:"

    # Get LLM response
    response = llm.predict(prompt)

    return response

# embed_all_books.py

import os
from dotenv import load_dotenv
import json
import numpy as np
import faiss
from openai import OpenAI

# --- Get the Key, testing and production ---
# For local testing
load_dotenv("GPT35.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Books to embed
books = {
    "slang_book": "book_pdf_pages_labeled.json",
    #"periodic_book": "book_pdf_pages_labeled.json",
    #"mysql_book": "book_pdf_pages_labeled.json",
    #"excel_book": "book_pdf_pages_labeled.json"
}

base_dir = "data"

for book_name, file_name in books.items():
    folder = os.path.join(base_dir, book_name)
    input_path = os.path.join(folder, file_name)
    faiss_out = os.path.join(folder, "book_pdf_index.faiss")
    meta_out = os.path.join(folder, "book_pdf_metadata.json")

    print(f"\n📚 Embedding: {book_name}")

    with open(input_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    embeddings = []
    metadata = []

    for i, entry in enumerate(pages):
        text = entry["text"].strip()
        if not text:
            continue

        # Create embedding
        try:
            emb = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            ).data[0].embedding
        except Exception as e:
            print(f"❌ Failed to embed chunk {i}: {e}")
            continue

        embeddings.append(emb)
        metadata.append(entry)

    # Save FAISS index
    if embeddings:
        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype("float32"))
        faiss.write_index(index, faiss_out)
        print(f"✅ FAISS index saved → {faiss_out}")

    # Save metadata
    with open(meta_out, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"✅ Metadata saved → {meta_out}")

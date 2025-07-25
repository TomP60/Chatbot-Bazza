# chunk_mysql_pdf.py

import fitz  # PyMuPDF
import json
import os

source_pdf = "source_docs/The MySQL Workshop.pdf"
output_folder = "data/mysql_book"
os.makedirs(output_folder, exist_ok=True)

doc = fitz.open(source_pdf)

pages = []
for i, page in enumerate(doc):
    text = page.get_text().strip()
    if text:
        pages.append({
            "page": str(i + 1),
            "pdf_page": i + 1,
            "text": text
        })

output_path = os.path.join(output_folder, "mysql_book_pdf_pages_labeled.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False, indent=2)

print(f"✅ Chunking complete: {len(pages)} pages saved to {output_path}")

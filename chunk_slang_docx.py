# chunk_slang_docx.py

from docx import Document
import json
import os

source_docx = "source_docs/Australian Slang Glossary.docx"
output_folder = "data/slang_book"
os.makedirs(output_folder, exist_ok=True)

doc = Document(source_docx)
entries = []

# Assume the glossary is in the first table
table = doc.tables[0]

for i, row in enumerate(table.rows[1:]):  # Skip header row
    word = row.cells[0].text.strip()
    meaning = row.cells[1].text.strip()
    if word and meaning:
        entries.append({
            "page": str(i + 1),  # Fake page number
            "pdf_page": i + 1,
            "text": f"{word}: {meaning}"
        })

output_path = os.path.join(output_folder, "book_pdf_pages_labeled.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"✅ Chunked {len(entries)} slang entries → {output_path}")

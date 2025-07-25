# chunk_periodic_glossary.py (robust version)

from docx import Document
import json
import os

source_docx = "source_docs/Glossary_PeriodTable.docx"
output_folder = "data/periodic_book"
os.makedirs(output_folder, exist_ok=True)

doc = Document(source_docx)
table = doc.tables[0]

chunks = []
i = 0
current_block = ""

for row in table.rows:
    cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]

    # Start of new element block: First cell repeated in second + description
    if len(cells) >= 3 and cells[0] == cells[1]:
        if current_block:
            chunks.append({
                "page": str(i + 1),
                "pdf_page": i + 1,
                "text": current_block.strip()
            })
            i += 1
        current_block = f"{cells[0]}: {cells[2]}"
    elif len(cells) >= 2:
        current_block += f"\n{cells[0]}: {cells[1]}"

# Final block
if current_block:
    chunks.append({
        "page": str(i + 1),
        "pdf_page": i + 1,
        "text": current_block.strip()
    })

output_path = os.path.join(output_folder, "book_pdf_pages_labeled.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"✅ Chunked {len(chunks)} elements → {output_path}")

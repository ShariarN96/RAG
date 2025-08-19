from pathlib import Path

from docling.document_converter import DocumentConverter

converter = DocumentConverter()

# --------------------------------------------------------------
# Basic PDF extraction
# --------------------------------------------------------------
pdf_dir = Path(__file__).parent.parent / "pdfs" / "test.pdf"
result = converter.convert(pdf_dir)

document = result.document
markdown_output = document.export_to_markdown()
json_output = document.export_to_dict()

print(markdown_output)

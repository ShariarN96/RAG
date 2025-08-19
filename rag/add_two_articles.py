from pathlib import Path
from typing import List

import lancedb
from dotenv import load_dotenv
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from openai import OpenAI
from transformers import AutoTokenizer

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Initialize tokenizer
hf_tok = AutoTokenizer.from_pretrained("bert-base-uncased", use_fast=True)
tokenizer = hf_tok
MAX_TOKENS = 4000

# Initialize chunker and converter
chunker = HybridChunker(tokenizer=tokenizer, max_tokens=MAX_TOKENS, merge_peers=True)
converter = DocumentConverter()

# List of PDF files to process
pdf_files = [
    Path(__file__).parent.parent / "pdfs" / "arzani.pdf",
    Path(__file__).parent.parent / "pdfs" / "test.pdf",
]

all_chunks = []

for pdf_path in pdf_files:
    result = converter.convert(pdf_path)
    chunk_iter = chunker.chunk(dl_doc=result.document)
    chunks = list(chunk_iter)
    for chunk in chunks:
        all_chunks.append(
            {
                "text": chunk.text,
                "metadata": {
                    "filename": chunk.meta.origin.filename,
                    "page_numbers": [
                        page_no
                        for page_no in sorted(
                            set(
                                prov.page_no
                                for item in chunk.meta.doc_items
                                for prov in item.prov
                            )
                        )
                    ]
                    or None,
                    "title": chunk.meta.headings[0] if chunk.meta.headings else None,
                },
            }
        )

# Connect to LanceDB and get embedding function
func = get_registry().get("openai").create(name="text-embedding-3-large")
db = lancedb.connect("data/lancedb")


# Define metadata and chunk schema
class ChunkMetadata(LanceModel):
    filename: str | None
    page_numbers: List[int] | None
    title: str | None


class Chunks(LanceModel):
    text: str = func.SourceField()
    vector: Vector(func.ndims()) = func.VectorField()  # type: ignore
    metadata: ChunkMetadata


# Create or overwrite the table and add all chunks
print(f"Adding {len(all_chunks)} chunks from 2 articles to the embedding table...")
table = db.create_table("docling", schema=Chunks, mode="overwrite")
table.add(all_chunks)
print("Done.")

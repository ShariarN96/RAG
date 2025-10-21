# from pathlib import Path
# from typing import List

# import lancedb
# from docling.chunking import HybridChunker
# from docling.document_converter import DocumentConverter
# from dotenv import load_dotenv
# from lancedb.embeddings import get_registry
# from lancedb.pydantic import LanceModel, Vector
# from openai import OpenAI
# import os
# from transformers import AutoTokenizer

# # from docling.tokenizers import OpenAITokenizerWrapper

# hf_tok = AutoTokenizer.from_pretrained("bert-base-uncased", use_fast=True)

# OpenAI_API_PATH = Path(__file__).parent.parent.parent / ".env"
# load_dotenv(OpenAI_API_PATH)
# OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# tokenizer = hf_tok
# # tokenizer = OpenAITokenizerWrapper()  # Load our custom tokenizer for OpenAI
# MAX_TOKENS = 2000  # text-embedding-3-large's maximum context length


# # --------------------------------------------------------------
# # Extract the data
# # --------------------------------------------------------------

# converter = DocumentConverter()

# # pdf_dir = Path(__file__).parent.parent.parent / "pdfs" / "test.pdf"
# file_dir = Path(__file__).parent.parent.parent.parent/'output.csv'
# result = converter.convert(file_dir)

# # result = converter.convert("https://arxiv.org/pdf/2408.09869")


# # --------------------------------------------------------------
# # Apply hybrid chunking
# # --------------------------------------------------------------

# chunker = HybridChunker(
#     tokenizer=tokenizer,
#     max_tokens=MAX_TOKENS,
#     merge_peers=True,
# )

# chunk_iter = chunker.chunk(dl_doc=result.document)
# chunks = list(chunk_iter)

# # --------------------------------------------------------------
# # Create a LanceDB database and table
# # --------------------------------------------------------------

# # Create a LanceDB database
# db = lancedb.connect("data/lancedb")


# # Get the OpenAI embedding function
# func = get_registry().get("openai").create(name="text-embedding-3-large")


# # Define a simplified metadata schema
# class ChunkMetadata(LanceModel):
#     """
#     You must order the fields in alphabetical order.
#     This is a requirement of the Pydantic implementation.
#     """

#     filename: str | None
#     page_numbers: List[int] | None
#     title: str | None


# # Define the main Schema
# class Chunks(LanceModel):
#     text: str = func.SourceField()
#     vector: Vector(func.ndims()) = func.VectorField()  # type: ignore
#     metadata: ChunkMetadata


# table = db.create_table("docling", schema=Chunks, mode="overwrite")

# # --------------------------------------------------------------
# # Prepare the chunks for the table
# # --------------------------------------------------------------

# # Create table with processed chunks
# processed_chunks = [
#     {
#         "text": chunk.text,
#         "metadata": {
#             "filename": chunk.meta.origin.filename,
#             "page_numbers": [
#                 page_no
#                 for page_no in sorted(
#                     set(
#                         prov.page_no
#                         for item in chunk.meta.doc_items
#                         for prov in item.prov
#                     )
#                 )
#             ]
#             or None,
#             "title": chunk.meta.headings[0] if chunk.meta.headings else None,
#         },
#     }
#     for chunk in chunks
# ]

# # --------------------------------------------------------------
# # Add the chunks to the table (automatically embeds the text)
# # --------------------------------------------------------------

# table.add(processed_chunks)

# # --------------------------------------------------------------
# # Load the table
# # --------------------------------------------------------------

# table.to_pandas()
# table.count_rows()


import json
import os
from pathlib import Path

import lancedb
import pandas as pd
from dotenv import load_dotenv
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

# Load CSV
file_path = Path(__file__).parent.parent.parent.parent / "output.csv"
df = pd.read_csv(file_path)


OpenAI_API_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(OpenAI_API_PATH)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")


# Connect LanceDB
db = lancedb.connect("data/lancedb")
func = get_registry().get("openai").create(name="text-embedding-3-large")


# Schema (metadata as string)
class Chunks(LanceModel):
    text: str = func.SourceField()
    vector: Vector(func.ndims()) = func.VectorField()
    metadata: str  # store metadata as JSON string


table = db.create_table("docling", schema=Chunks, mode="overwrite")

# Process rows
processed_chunks = []
for _, row in df.iterrows():
    row_text = " | ".join(
        [f"{col}: {str(val)}" for col, val in row.items() if pd.notnull(val)]
    )
    processed_chunks.append(
        {
            "text": row_text,
            "metadata": json.dumps(row.to_dict()),  # store entire row as JSON string
        }
    )

table.add(processed_chunks)

print("Row count:", table.count_rows())
print(table.to_pandas().head())


z = table.to_pandas()
table.count_rows()

from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from openai import OpenAI
from transformers import AutoTokenizer

load_dotenv()

# Initialize OpenAI client (make sure you have OPENAI_API_KEY in your environment variables)
client = OpenAI()


hf_tok = AutoTokenizer.from_pretrained(
    "bert-base-uncased", use_fast=True
)  # Load our custom tokenizer for OpenAI
MAX_TOKENS = 8191  # text-embedding-3-large's maximum context length


# --------------------------------------------------------------
# Extract the data
# --------------------------------------------------------------

converter = DocumentConverter()
# result = converter.convert("https://arxiv.org/pdf/2408.09869")

pdf_dir = Path(__file__).parent.parent / "pdfs" / "test.pdf"
result = converter.convert(pdf_dir)


# --------------------------------------------------------------
# Apply hybrid chunking
# --------------------------------------------------------------


chunker = HybridChunker(
    tokenizer=hf_tok,
    max_tokens=MAX_TOKENS,
    merge_peers=True,
)

chunk_iter = chunker.chunk(dl_doc=result.document)
chunks = list(chunk_iter)

len(chunks)

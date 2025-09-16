from pathlib import Path

import tiktoken
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer
from dotenv import load_dotenv
from openai import OpenAI

OpenAI_API_PATH = Path(__file__).parent.parent.parent / ".env"
OPENAI_KEY = load_dotenv(OpenAI_API_PATH)

# Initialize OpenAI client (make sure you have OPENAI_API_KEY in your environment variables)
client = OpenAI(api_key=OPENAI_KEY)

MAX_TOKENS = 8191


# --------------------------------------------------------------
# Extract the data
# --------------------------------------------------------------

converter = DocumentConverter()


tokenizer = OpenAITokenizer(
    tokenizer=tiktoken.encoding_for_model("gpt-4o"),
    max_tokens=128 * 1024,  # context window length required for OpenAI tokenizers
)

current_dir = Path(__file__)


def chunks_from_pdf():
    pdf_dir = current_dir.parent.parent.parent.parent / "pdfs" / "test.pdf"
    result = converter.convert(pdf_dir)

    chunker = HybridChunker(
        max_tokens=MAX_TOKENS,
        tokenizer=tokenizer,
        merge_peers=True,
    )

    chunk_iter = chunker.chunk(dl_doc=result.document)
    chunks = list(chunk_iter)
    len(chunks)

    return chunks

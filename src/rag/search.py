# qa_from_pdf_no_vectors.py
# pip install docling transformers dotenv openai

import json
import os
import re
from pathlib import Path
from typing import List

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from openai import OpenAI
from transformers import AutoTokenizer

# ========= CONFIG =========
PDF_PATH = Path(__file__).parent.parent.parent / "pdfs" / "test.pdf"

# Your question (put anything you want here)
QUESTION = (
    "Identify the reaction (OER, HER, ORR, NO3RR, CO2 reduction) studied in this paper. "
    "Identify the catalyst material studied in this paper. "
    "What is the organic linker of the catalyst"
    "Is it single metal or binary>ternary?"
    "Is it acmorphous or crystalline?"
    "What is the stability results of the catalyst"
    "Extract the OER/HER/ORR/NO3RR key performance metrics and  "
    "(overpotential at 10 mA cm^-2, Tafel slope, electrolyte, pH, temperature, loading, Faradaic efficiency) "
    "from this paper and return a tidy JSON list. If a field is missing, use null. "
    "Be precise and use only the context I supply."
)

# OpenAI models
CHAT_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.7

# Chunking (no embeddings here)
MAX_TOKENS_PER_CHUNK = 1200  # keep chunks small enough for prompt + question
TOP_K = 6  # how many chunks to send to the model

# Optional: heuristic keywords to score chunks against your question/domain
DEFAULT_KEYWORDS = [
    "overpotential",
    "tafel",
    "mA cm",
    "electrolyte",
    "pH",
    "temperature",
    "loading",
    "faradaic",
    "efficiency",
    "NO3RR",
    "nitrate",
    "ammonia",
    "OER",
    "ORR",
    "HER",
    "current density",
    "onset",
    "rhe",
    "ag/agcl",
    "mV/dec",
    "mV",
    "kOH",
    "h2so4",
]
# ==========================


def ensure_api_key():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Missing OPENAI_API_KEY; set it in your env or .env file.")


def convert_pdf_to_chunks(pdf_path: Path):
    """
    Convert PDF -> Docling doc -> text chunks (no embeddings).
    Returns a list of dicts: {text, metadata{filename, page_numbers, title}}
    """
    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))

    # Use any tokenizer (HF is fine); we only need token counts for chunk sizing
    hf_tok = AutoTokenizer.from_pretrained("bert-base-uncased", use_fast=True)
    chunker = HybridChunker(
        tokenizer=hf_tok,
        max_tokens=MAX_TOKENS_PER_CHUNK,
        merge_peers=True,
    )

    processed = []
    for ch in chunker.chunk(dl_doc=result.document):
        # gather page numbers from provenance if available
        try:
            pages = sorted(
                {prov.page_no for item in ch.meta.doc_items for prov in item.prov}
            )
        except Exception:
            pages = None

        processed.append(
            {
                "text": ch.text or "",
                "metadata": {
                    "filename": (
                        ch.meta.origin.filename if ch.meta and ch.meta.origin else None
                    ),
                    "page_numbers": pages or None,
                    "title": (
                        ch.meta.headings[0] if ch.meta and ch.meta.headings else None
                    ),
                },
            }
        )
    return processed


def keywords_from_question(q: str) -> List[str]:
    # build a light keyword list from the question + defaults
    toks = re.findall(r"[a-zA-Z0-9\-/\+\.%]+", q.lower())
    toks = [t for t in toks if len(t) >= 3]
    # merge with domain defaults
    bag = set(DEFAULT_KEYWORDS) | set(toks)
    return list(bag)


def score_chunk(text: str, kws: List[str]) -> float:
    # very simple scoring: sum of occurrences (case-insensitive)
    s = text.lower()
    return sum(s.count(k.lower()) for k in kws)


def pick_top_chunks(chunks: List[dict], question: str, k: int) -> List[dict]:
    kws = keywords_from_question(question)
    scored = [(score_chunk(c["text"], kws), idx) for idx, c in enumerate(chunks)]
    scored.sort(reverse=True)
    # If everything scores 0 (rare), fallback to longest chunks
    if all(sc[0] == 0 for sc in scored):
        scored = [(-len(chunks[idx]["text"]), idx) for _, idx in scored]
        scored.sort()  # most negative (longest) first
    top = [chunks[idx] for _, idx in scored[:k]]
    return top


def build_context(top_chunks: List[dict]) -> str:
    """
    Build a readable context with inline source info; the model will see sources as text.
    """
    blocks = []
    for i, c in enumerate(top_chunks, start=1):
        meta = c["metadata"] or {}
        src = []
        if meta.get("filename"):
            src.append(str(meta["filename"]))
        if meta.get("page_numbers"):
            src.append("p. " + ", ".join(str(p) for p in meta["page_numbers"]))
        if not src:
            src = ["(unknown source)"]
        title = meta.get("title") or "(untitled section)"
        blocks.append(
            f"[SOURCE {i}] {' - '.join(src)}\nTitle: {title}\n\n{c['text']}\n"
        )
    return "\n\n---\n\n".join(blocks)


API_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(API_PATH)
api_key1 = os.getenv("OPENAI_API_KEY")


def ask_llm(question: str, context: str) -> str:
    """
    Send one chat completion with a strict instruction to use only the provided context.
    """
    client = OpenAI(api_key=api_key1)
    system_prompt = """You are a helpful assistant that answers questions based on the provided context.
    Use only the information from the context to answer questions. If you're unsure or the context
    doesn't contain the relevant information, say so
        "Use ONLY the supplied context to answer. 
        "If data are missing, return null for those fields. 

        "Prefer values reported at 10 mA cm^-2 for overpotential and report Tafel in mV/dec."""

    user_prompt = f"""Context:{context}

    Task:
    {question}

    Return only the answer (no extra commentary)."""

    rsp = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return rsp.choices[0].message.content.strip()


def main():
    # ensure_api_key()

    print(f"Reading PDF: {PDF_PATH}")
    chunks = convert_pdf_to_chunks(PDF_PATH)
    if not chunks:
        raise RuntimeError(
            "No chunks extracted; check your PDF path or Docling install."
        )

    print(f"Total chunks: {len(chunks)}")
    top_chunks = pick_top_chunks(chunks, QUESTION, TOP_K)
    context = build_context(top_chunks)

    # print("\nSelected sources:\n")
    # for i, c in enumerate(top_chunks, start=1):
    #     md = c["metadata"]
    #     fn = md.get("filename") or "(unknown)"
    #     pages = md.get("page_numbers")
    #     title = md.get("title") or "(untitled)"
    #     page_str = f"p. {', '.join(map(str, pages))}" if pages else "p. ?"
    #     print(f"  [{i}] {fn} — {page_str} — {title}")

    print("\nAsking the model...\n")
    answer = ask_llm(QUESTION, context)

    # Try to pretty-print JSON if the answer is JSON
    try:
        parsed = json.loads(answer)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except Exception:
        print(answer)


if __name__ == "__main__":
    main()


print(f"Reading PDF: {PDF_PATH}")
chunks = convert_pdf_to_chunks(PDF_PATH)
if not chunks:
    raise RuntimeError("No chunks extracted; check your PDF path or Docling install.")

print(f"Total chunks: {len(chunks)}")
top_chunks = pick_top_chunks(chunks, QUESTION, TOP_K)
context = build_context(top_chunks)

# print("\nSelected sources:\n")
# for i, c in enumerate(top_chunks, start=1):
#     md = c["metadata"]
#     fn = md.get("filename") or "(unknown)"
#     pages = md.get("page_numbers")
#     title = md.get("title") or "(untitled)"
#     page_str = f"p. {', '.join(map(str, pages))}" if pages else "p. ?"
#     print(f"  [{i}] {fn} — {page_str} — {title}")
QUESTION = "What is the stability and durability of the catalyst, find details and quantitative data if available. how long and under what electrochemical condition did they test"
QUESTION = "what is the long term stability result of the mof in the paper"
QUESTION = "give a summary of the article"
answer = ask_llm(QUESTION, context)
answer
# Try to pretty-print JSON if the answer is JSON


# print(json.dumps(answer, indent=4))

cleaned = answer.replace("```json", "").replace("```", "").strip()
try:
    parsed = json.loads(cleaned)
    print(json.dumps(parsed, indent=4, ensure_ascii=False))
except Exception:
    print(cleaned)
qq = "what is the stability results of the catalyst, how long? how many hours or minutes?"
top_chunks = pick_top_chunks(chunks, qq, TOP_K)
context = build_context(top_chunks)


def ask_question_simple(question: str, context: str = ""):
    """
    Ask the LLM a question and return the answer, pretty-printing JSON if possible.
    Cleans markdown code blocks if present in the answer.
    """
    answer = ask_llm(question, context)
    # Remove markdown code block formatting if present
    cleaned = answer.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
        print(json.dumps(parsed, indent=4, ensure_ascii=False))
        return parsed
    except Exception:
        print(cleaned)
        return cleaned


z = ask_question_simple(qq, context)

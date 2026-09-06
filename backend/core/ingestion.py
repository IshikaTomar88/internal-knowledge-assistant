"""core/ingestion.py — PDF extraction and chunking, isolated from routing."""
import re
from io import BytesIO
from typing import List

import pdfplumber

from config.prompts import CHUNK_SIZE, CHUNK_OVERLAP


def extract_pages(file_bytes: bytes) -> List[tuple]:
    pages = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages.append((i + 1, text))
    return pages


def chunk_pages(pages: List[tuple], source: str) -> List[dict]:
    chunks = []
    for page_num, text in pages:
        words = re.sub(r"\s+", " ", text).strip().split(" ")
        i = 0
        while i < len(words):
            piece = " ".join(words[i:i + CHUNK_SIZE]).strip()
            if piece:
                chunks.append({"text": piece, "source": source, "page": page_num})
            i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

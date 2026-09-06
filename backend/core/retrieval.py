"""core/retrieval.py — vector-style retrieval (TF-IDF) + answer generation."""
import os
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config.prompts import RAG_SYSTEM_PROMPT, MIN_SIMILARITY, TOP_K

# In-memory store — swap for Supabase/pgvector or ChromaDB/FAISS in production
CHUNKS: List[dict] = []
DOCS: List[str] = []


def add_chunks(chunks: List[dict], source_name: str) -> None:
    CHUNKS.extend(chunks)
    if source_name not in DOCS:
        DOCS.append(source_name)


def retrieve(query: str, top_k: int = TOP_K) -> List[dict]:
    if not CHUNKS:
        return []
    texts = [c["text"] for c in CHUNKS]
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(texts + [query])
    except ValueError:
        return []
    sims = cosine_similarity(matrix[-1:], matrix[:-1]).flatten()
    ranked = sorted(zip(sims, CHUNKS), key=lambda x: x[0], reverse=True)
    return [c for score, c in ranked[:top_k] if score >= MIN_SIMILARITY]


def generate_answer(query: str, retrieved: List[dict]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    context = "\n\n".join(f"[{c['source']}, p.{c['page']}] {c['text']}" for c in retrieved)

    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
                ],
                max_tokens=200,
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    if retrieved:
        return retrieved[0]["text"][:400]
    return "This document doesn't appear to cover that — I don't want to guess. Try rephrasing, or ask something else covered in the uploaded file."

"""main.py — Entry point. Route definitions only; all logic lives in core/."""
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.ingestion import extract_pages, chunk_pages
from core.retrieval import add_chunks, retrieve, generate_answer, CHUNKS, DOCS

app = FastAPI(title="RAG Document Q&A API", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class SourceOut(BaseModel):
    source: str
    page: Optional[int]
    excerpt: str


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceOut]


@app.get("/")
def root():
    return {"status": "ok", "service": "rag-document-qa"}


@app.get("/status")
def status():
    return {"documents": DOCS, "chunks_indexed": len(CHUNKS)}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are supported.")

    file_bytes = await file.read()
    try:
        pages = extract_pages(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Couldn't read PDF: {e}")

    if not pages:
        raise HTTPException(status_code=422, detail="No extractable text found — is this a scanned/image PDF?")

    new_chunks = chunk_pages(pages, file.filename)
    add_chunks(new_chunks, file.filename)

    return {"ok": True, "filename": file.filename, "pages": len(pages), "chunks_added": len(new_chunks)}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    if not CHUNKS:
        raise HTTPException(status_code=400, detail="No documents indexed yet — upload a PDF first.")

    retrieved = retrieve(req.question)
    answer = generate_answer(req.question, retrieved)
    sources = [SourceOut(source=c["source"], page=c["page"], excerpt=c["text"][:180]) for c in retrieved]
    return AskResponse(answer=answer, sources=sources)

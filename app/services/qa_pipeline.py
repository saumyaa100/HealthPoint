from app.services.pdf_loader import download_pdf, extract_text_from_pdf_bytes, chunk_text
from app.services.embedding_store import build_embeddings_and_store, query_top_k
from app.services.llm_service import generate_answer
from app.utils.logger import get_logger
import app.config as cfg

logger = get_logger(__name__)

def answer_questions_from_document(document_url: str, questions: list):
    """
    Full orchestrator:
    - Download PDF
    - Extract text
    - Chunk text
    - Create embeddings (in-memory or pinecone)
    - For each question: retrieve top-k chunks, call LLM, collect answers
    """
    pdf_bytes = download_pdf(document_url)
    text = extract_text_from_pdf_bytes(pdf_bytes)
    chunks = chunk_text(text, chunk_size=cfg.CHUNK_SIZE, chunk_overlap=cfg.CHUNK_OVERLAP)

    # Build embeddings & store them (so query_top_k can search)
    build_embeddings_and_store(chunks, embed_model=cfg.OPENAI_EMBED_MODEL)

    answers = []
    for q in questions:
        hits = query_top_k(q, embed_model=cfg.OPENAI_EMBED_MODEL, top_k=cfg.TOP_K)
        # hits format: list of (metadata, score) or (metadata, score) depending on store
        context_chunks = []
        for meta, score in hits:
            # meta expected to have 'text' & 'id'
            if isinstance(meta, dict) and "text" in meta:
                context_chunks.append({"id": meta.get("id"), "text": meta.get("text")})
        # generate answer with LLM
        if not context_chunks:
            answers.append("Not found in document.")
        else:
            ans = generate_answer(q, context_chunks)
            answers.append(ans)
    return answers

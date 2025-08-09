import requests
from pypdf import PdfReader
from io import BytesIO
from app.utils.logger import get_logger

logger = get_logger(__name__)

def download_pdf(url: str, timeout: int = 20) -> bytes:
    """
    Download PDF bytes from a URL.
    """
    logger.info(f"Downloading PDF from {url}")
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "")
    if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
        logger.warning("URL does not have pdf content-type; continuing anyway.")
    return resp.content

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using pypdf.
    """
    logger.info("Extracting text from PDF bytes")
    reader = PdfReader(BytesIO(pdf_bytes))
    text_parts = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
            text_parts.append(text)
        except Exception as e:
            logger.warning(f"Failed to extract page text: {e}")
    full_text = "\n".join(text_parts)
    logger.info(f"Extracted {len(full_text)} characters from PDF")
    return full_text

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Simple character-based chunking with overlap.
    Returns list of dicts: {id: int, text: str}
    """
    if not text:
        return []
    chunks = []
    start = 0
    idx = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({"id": idx, "text": chunk_text})
            idx += 1
        start += (chunk_size - chunk_overlap)
    return chunks

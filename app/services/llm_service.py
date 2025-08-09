import openai
from app.utils.logger import get_logger
import app.config as cfg

logger = get_logger(__name__)
openai.api_key = cfg.OPENAI_API_KEY

SYSTEM_PROMPT = (
    "You are an expert insurance policy assistant. Answer concisely and cite (copy) the "
    "relevant excerpt(s) from the provided document chunks when possible. If the document does not "
    "contain the information, say 'Not found in document.' Keep answers objective and policy-focused."
)

def generate_answer(question: str, context_chunks: list, model: str = None, temperature: float = 0.0, max_tokens: int = 512):
    """
    Calls OpenAI chat completion (gpt-4) with context chunks.
    context_chunks: list of dicts with 'text' and optionally 'id'
    """
    if model is None:
        model = cfg.OPENAI_CHAT_MODEL

    # Build context string
    context_text = "\n\n---\n\n".join([f"Chunk {c.get('id', '?')}: {c['text']}" for c in context_chunks])

    prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}\n\nAnswer concisely and mention the chunk numbers where you found the information."}
    ]

    logger.info("Calling OpenAI ChatCompletion for question")
    resp = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    content = resp["choices"][0]["message"]["content"].strip()
    return content

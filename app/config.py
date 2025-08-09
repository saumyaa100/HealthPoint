import os
from dotenv import load_dotenv

load_dotenv()

# App auth key (simple bearer to protect endpoint)
API_KEY = os.getenv("API_KEY", "change_me")

# OpenAI config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Pinecone (optional). If not provided, fallback to local similarity search.
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENV = os.getenv("PINECONE_ENV", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "hackrx-index")

# Processing defaults
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
TOP_K = int(os.getenv("TOP_K", 3))

# OpenAI model for completion and embeddings
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4")

print("Loaded API_KEY:", API_KEY)

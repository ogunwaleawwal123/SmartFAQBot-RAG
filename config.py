import os

from dotenv import load_dotenv

# ==========================================
# Load Environment
# ==========================================

load_dotenv()

# ==========================================
# Discord
# ==========================================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Comma-separated role IDs in .env
# Example:
# MODERATOR_ROLE_IDS=123456789012345678,987654321098765432

_role_ids = os.getenv("MODERATOR_ROLE_IDS", "")

MODERATOR_ROLE_IDS = [
    int(role.strip())
    for role in _role_ids.split(",")
    if role.strip().isdigit()
]

# ==========================================
# Groq
# ==========================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "llama-3.3-70b-versatile"
)

TEMPERATURE = float(
    os.getenv("TEMPERATURE", "0.1")
)

MAX_TOKENS = int(
    os.getenv("MAX_TOKENS", "700")
)

# ==========================================
# ChromaDB
# ==========================================

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "database"
)

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "dna_faq"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5"
)

# ==========================================
# Memory
# ==========================================

MEMORY_TIMEOUT = int(
    os.getenv("MEMORY_TIMEOUT", "900")
)

# ==========================================
# Cache
# ==========================================

CACHE_TTL = int(
    os.getenv("CACHE_TTL", "3600")
)

CACHE_SIZE = int(
    os.getenv("CACHE_SIZE", "500")
)
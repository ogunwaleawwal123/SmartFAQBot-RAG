import chromadb

from chromadb.utils import embedding_functions

from config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)

# ==========================================
# Read FAQ
# ==========================================

with open(
    "faq.txt",
    "r",
    encoding="utf-8"
) as f:

    faq_text = f.read()

faq_chunks = [
    chunk.strip()
    for chunk in faq_text.split("---")
    if chunk.strip()
]

# ==========================================
# Chroma
# ==========================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

embedding_function = (
    embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function
)

# ==========================================
# Rebuild Index
# ==========================================

existing = collection.get()

if existing["ids"]:
    collection.delete(
        ids=existing["ids"]
    )

collection.add(
    ids=[
        str(i)
        for i in range(len(faq_chunks))
    ],
    documents=faq_chunks
)

print("=" * 50)
print(f"Indexed {len(faq_chunks)} FAQ entries.")
print("Database rebuilt successfully.")
print("=" * 50)
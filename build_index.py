import chromadb
from chromadb.utils import embedding_functions

# Read the FAQ file
with open("faq.txt", "r", encoding="utf-8") as f:
    faq_text = f.read()

# Split FAQs using the separator
faq_list = [x.strip() for x in faq_text.split("---") if x.strip()]

# Create Chroma client
client = chromadb.PersistentClient(path="database")

# Embedding model
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-en-v1.5"
)

# Create collection
collection = client.get_or_create_collection(
    name="dna_faq",
    embedding_function=embedding_function
)

# Clear old data if it exists
try:
    collection.delete(ids=[str(i) for i in range(10000)])
except:
    pass

# Add FAQs
for i, faq in enumerate(faq_list):
    collection.add(
        documents=[faq],
        ids=[str(i)]
    )

print(f"✅ Indexed {len(faq_list)} FAQs successfully!")
import hashlib
import re

import chromadb

from chromadb.utils import embedding_functions
from rapidfuzz import process, fuzz

from config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)

from synonyms import SYNONYMS

# ==========================================================
# Chroma
# ==========================================================

embedding_function = (
    embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
)

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function
)

# ==========================================================
# Load FAQ
# ==========================================================

with open(
    "faq.txt",
    "r",
    encoding="utf-8"
) as f:

    FAQ_TEXT = f.read()

FAQ_LIST = [
    x.strip()
    for x in FAQ_TEXT.split("---")
    if x.strip()
]

# ==========================================================
# Normalize
# ==========================================================

def normalize(text: str):

    text = text.lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text
    )

    # Synonym expansion
    for old, new in SYNONYMS.items():

        text = text.replace(
            old,
            new
        )

    return " ".join(text.split())


# ==========================================================
# Semantic Search
# ==========================================================

def semantic_search(
    question,
    n_results=15
):

    results = collection.query(
        query_texts=[
            normalize(question)
        ],
        n_results=n_results,
        include=[
            "documents",
            "distances"
        ]
    )

    docs = results["documents"][0]
    distances = results["distances"][0]

    ranked = []

    for doc, distance in zip(
        docs,
        distances
    ):

        similarity = 1 - distance

        # Filter weak matches
        if similarity >= 0.22:

            ranked.append(
                (
                    similarity,
                    doc
                )
            )

    ranked.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [
        doc
        for _, doc in ranked
    ]


# ==========================================================
# Keyword Boost
# ==========================================================

def keyword_boost(question):

    q = normalize(question)

    boosted = []

    for faq in FAQ_LIST:

        score = 0

        faq_norm = normalize(faq)

        for word in q.split():

            if len(word) < 3:
                continue

            if word in faq_norm:
                score += 1

        if score >= 2:
            boosted.append(
                (
                    score,
                    faq
                )
            )

    boosted.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [
        faq
        for _, faq in boosted[:8]
    ]
# ==========================================================
# Fuzzy Search
# ==========================================================

def fuzzy_search(
    question,
    limit=10
):

    normalized_faq = [
        normalize(faq)
        for faq in FAQ_LIST
    ]

    matches = process.extract(
        normalize(question),
        normalized_faq,
        scorer=fuzz.token_set_ratio,
        limit=limit
    )

    docs = []

    for _, score, index in matches:

        if score >= 55:

            docs.append(
                FAQ_LIST[index]
            )

    return docs


# ==========================================================
# Merge & Deduplicate
# ==========================================================

def merge_results(*groups):

    combined = []
    seen = set()

    for group in groups:

        for doc in group:

            key = hashlib.md5(
                doc.lower().strip().encode("utf-8")
            ).hexdigest()

            if key in seen:
                continue

            seen.add(key)

            combined.append(doc)

    return combined


# ==========================================================
# Final Ranking
# ==========================================================

def rerank(question, docs):

    q = normalize(question)

    scored = []

    for doc in docs:

        score = fuzz.token_set_ratio(
            q,
            normalize(doc)
        )

        # Reward FAQs that contain multiple keywords
        bonus = 0

        for word in q.split():

            if len(word) >= 3 and word in normalize(doc):
                bonus += 2

        scored.append(
            (
                score + bonus,
                doc
            )
        )

    scored.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [
        doc
        for _, doc in scored
    ]


# ==========================================================
# Main Retrieval
# ==========================================================

def retrieve(question):

    semantic = semantic_search(question)

    fuzzy = fuzzy_search(question)

    keyword = keyword_boost(question)

    merged = merge_results(
        semantic,
        fuzzy,
        keyword
    )

    ranked = rerank(
        question,
        merged
    )

    # Return only the strongest matches
    top_chunks = ranked[:8]

    context = "\n\n----------------------\n\n".join(
        top_chunks
    )

    return context, top_chunks
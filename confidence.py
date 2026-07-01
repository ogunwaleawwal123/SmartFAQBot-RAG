from typing import List


MIN_CONTEXT_CHUNKS = 2
MIN_CONTEXT_LENGTH = 300


def has_enough_context(context: str) -> bool:
    """
    Returns True if the retrieved FAQ context appears sufficient
    to answer the question.
    """

    if not context:
        return False

    if len(context.strip()) < MIN_CONTEXT_LENGTH:
        return False

    return True


def context_score(chunks: List[str]) -> float:
    """
    Gives a simple confidence score from 0.0 to 1.0
    based on the retrieved FAQ chunks.
    """

    if not chunks:
        return 0.0

    score = min(len(chunks), 5) / 5

    avg_length = sum(len(c) for c in chunks) / len(chunks)

    if avg_length > 500:
        score += 0.15

    return min(score, 1.0)


def should_fallback(context: str, chunks: List[str]) -> bool:
    """
    Determines whether the bot should avoid answering.
    """

    if not has_enough_context(context):
        return True

    if context_score(chunks) < 0.40:
        return True

    return False
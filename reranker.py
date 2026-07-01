from rapidfuzz import fuzz


def rerank(question: str, documents: list[str]) -> list[str]:
    """
    Re-rank retrieved FAQ documents so the most relevant
    ones are placed first.
    """

    scored = []

    question = question.lower()

    for doc in documents:

        score = fuzz.token_set_ratio(
            question,
            doc.lower()
        )

        scored.append(
            (score, doc)
        )

    scored.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [
        doc
        for _, doc in scored
    ]
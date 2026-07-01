import time

from groq import Groq

from config import (
    GROQ_API_KEY,
    LLM_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
)

from prompts import SYSTEM_PROMPT
from retriever import retrieve

from memory import (
    get as get_history,
    add as add_history,
    last_user_message,
)

from cache import (
    get as get_cache,
    save as save_cache,
)

client = Groq(api_key=GROQ_API_KEY)


def ask_groq(user_id: int, question: str):

    start = time.time()

    # -----------------------------------------
    # Cache
    # -----------------------------------------

    cached = get_cache(question)

    if cached:
        print(f"[CACHE] {time.time()-start:.2f}s")
        return cached

    # -----------------------------------------
    # Improve follow-up retrieval
    # -----------------------------------------

    previous = last_user_message(user_id)

    search_query = question

    if previous:

        # If the new message is short,
        # assume it is a follow-up.
        if len(question.split()) <= 8:

            search_query = (
                previous
                + "\n"
                + question
            )

    # -----------------------------------------
    # Retrieve FAQ
    # -----------------------------------------

    context, chunks = retrieve(search_query)

    # Save user's question immediately
    add_history(
        user_id,
        "user",
        question
    )

    if not chunks:

        add_history(
            user_id,
            "assistant",
            "NOT_FOUND"
        )

        return "NOT_FOUND"

    history = get_history(user_id)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": f"FAQ CONTEXT\n\n{context}"
        }
    ]

    messages.extend(history)

    groq_start = time.time()

    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        messages=messages
    )

    print(f"[GROQ] {time.time()-groq_start:.2f}s")

    answer = response.choices[0].message.content.strip()

    if answer != "NOT_FOUND":

        lower = answer.lower()

        bad_phrases = [

            "not explicitly mentioned",

            "there is no information",

            "not stated",

            "based on the available information",

            "i cannot find",

        ]

        if any(x in lower for x in bad_phrases):

            answer = "NOT_FOUND"

    add_history(
        user_id,
        "assistant",
        answer
    )
    print(f"[MEMORY] User {user_id} has {len(get_history(user_id))} messages stored.")

    if answer != "NOT_FOUND":

        save_cache(
            question,
            answer
        )

    print(f"[TOTAL] {time.time()-start:.2f}s")

    return answer
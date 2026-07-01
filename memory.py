from collections import defaultdict, deque
import time

MEMORY_TIMEOUT = 900
MAX_HISTORY = 12

MEMORY = defaultdict(lambda: deque(maxlen=MAX_HISTORY))
LAST_ACTIVITY = {}


def cleanup():

    now = time.time()

    expired = []

    for user_id, last in LAST_ACTIVITY.items():
        if now - last > MEMORY_TIMEOUT:
            expired.append(user_id)

    for user_id in expired:
        MEMORY.pop(user_id, None)
        LAST_ACTIVITY.pop(user_id, None)


def add(user_id: int, role: str, content: str):

    cleanup()

    MEMORY[user_id].append({
        "role": role,
        "content": content
    })

    LAST_ACTIVITY[user_id] = time.time()


def get(user_id: int):

    cleanup()

    LAST_ACTIVITY[user_id] = time.time()

    return list(MEMORY[user_id])


def last_user_message(user_id: int):

    cleanup()

    if user_id not in MEMORY:
        return None

    for message in reversed(MEMORY[user_id]):

        if message["role"] == "user":
            return message["content"]

    return None


def clear(user_id: int):

    MEMORY.pop(user_id, None)
    LAST_ACTIVITY.pop(user_id, None)


def clear_all():

    MEMORY.clear()
    LAST_ACTIVITY.clear()
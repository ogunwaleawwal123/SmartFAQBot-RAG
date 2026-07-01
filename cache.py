import time

# ==========================================
# Settings
# ==========================================

CACHE_TTL = 3600      # 1 hour
MAX_CACHE_SIZE = 500

# ==========================================
# Cache Storage
# ==========================================

CACHE = {}

# ==========================================
# Cleanup
# ==========================================

def cleanup():

    now = time.time()

    expired = []

    for question, (_, timestamp) in CACHE.items():

        if now - timestamp > CACHE_TTL:
            expired.append(question)

    for question in expired:
        CACHE.pop(question, None)

# ==========================================
# Get
# ==========================================

def get(question: str):

    cleanup()

    key = question.lower().strip()

    if key not in CACHE:
        return None

    answer, _ = CACHE[key]

    return answer

# ==========================================
# Save
# ==========================================

def save(question: str, answer: str):

    cleanup()

    if len(CACHE) >= MAX_CACHE_SIZE:

        oldest = min(
            CACHE.items(),
            key=lambda x: x[1][1]
        )[0]

        CACHE.pop(oldest)

    CACHE[
        question.lower().strip()
    ] = (
        answer,
        time.time()
    )

# ==========================================
# Clear
# ==========================================

def clear():

    CACHE.clear()

# ==========================================
# Size
# ==========================================

def size():

    cleanup()

    return len(CACHE)
import os
import json
import hashlib
import discord
import chromadb

from groq import Groq
from dotenv import load_dotenv
from rapidfuzz import process, fuzz
from discord.ext import commands
from chromadb.utils import embedding_functions

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq = Groq(api_key=GROQ_API_KEY)

# -----------------------
# Discord
# -----------------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# -----------------------
# ChromaDB
# -----------------------

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-en-v1.5"
)

db = chromadb.Client()

collection = db.get_collection(
    name="dna_faq",
    embedding_function=embedding_function
)

# -----------------------
# FAQ TEXT
# -----------------------

with open("faq.txt", "r", encoding="utf-8") as f:
    FAQ_TEXT = f.read()

FAQ_LIST = [
    x.strip()
    for x in FAQ_TEXT.split("---")
    if x.strip()
]

# -----------------------
# Cache
# -----------------------

CACHE = {}

# -----------------------
# Settings
# -----------------------

MOD_CHANNEL = 1435468208319500289

FALLBACK = (
    "I couldn't confidently find an answer to that in the current DNA Funded FAQ. 😊\n\n"
    f"For an official answer, please ask in <#{MOD_CHANNEL}> where a moderator will assist you."
)

SYSTEM_PROMPT = """
You are DNA Funded's Smart FAQ Assistant.

Your personality:

- Friendly.
- Professional.
- Human.
- Never robotic.
- Match the user's tone.
- Understand slang.
- Understand abbreviations.
- Understand spelling mistakes.
- Use emojis naturally and sparingly to make replies feel friendly.
- Only use emojis when they genuinely improve readability or tone.
- Avoid excessive or repetitive emojis.
- Professional answers do not always need emojis only if it makes it more professional.

Rules:

Answer ONLY using the FAQ context provided.

Never invent policies.

Never guess.

If the FAQ does not contain enough information,
reply ONLY with:

NOT_FOUND

When the answer exists:

• Start with a clear and direct answer.

• Then explain it naturally like an experienced DNA Funded moderator helping a member.

• Be precise, informative and easy to understand.

• Give enough detail for the member to understand the rule, but avoid unnecessary repetition or overly long explanations.

• When appropriate, include a short practical example using a $10,000 account or a realistic trading scenario to help the member understand the rule.

• Only use examples when they genuinely make the explanation clearer.

• Combine related FAQ information whenever it improves the answer.

• Break answers into short paragraphs with a blank line between ideas.

• Use bullet points for lists, challenge comparisons, percentages, limits, requirements or multiple conditions.

• Never reply with only "Yes" or "No" unless the FAQ truly contains nothing more.

• Never invent examples or information that contradict the FAQ.

• Never mention the FAQ, retrieved context or how you found the answer.

Aim to sound like a knowledgeable human moderator.

Keep answers concise but complete. Most replies should naturally be between 100 and 250 words. Only go longer when the topic genuinely requires it.
"""
# -----------------------
# Hybrid Search
# -----------------------

def semantic_search(question, n_results=12):

    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )

    docs = results.get("documents", [[]])[0]

    return docs


def fuzzy_search(question, limit=8):

    matches = process.extract(
        question,
        FAQ_LIST,
        scorer=fuzz.token_set_ratio,
        limit=limit
    )

    docs = []

    for text, score, _ in matches:
        if score >= 45:
            docs.append(text)

    return docs


def retrieve_context(question):

    semantic = semantic_search(question)

    fuzzy = fuzzy_search(question)

    combined = []

    seen = set()

    for doc in semantic + fuzzy:

        key = hashlib.md5(
            doc.encode("utf-8")
        ).hexdigest()

        if key not in seen:

            seen.add(key)

            combined.append(doc)

    return "\n\n----------------------\n\n".join(combined)


# -----------------------
# Groq
# -----------------------

def ask_groq(question):

    cache_key = question.lower().strip()

    if cache_key in CACHE:

        return CACHE[cache_key]

    context = retrieve_context(question)

    response = groq.chat.completions.create(

        model="llama-3.3-70b-versatile",

        temperature=0.35,

        max_tokens=1200,

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "system",
                "content":
                f"""
FAQ CONTEXT

{context}
"""
            },

            {
                "role": "user",
                "content": question
            }

        ]
    )

    answer = response.choices[0].message.content.strip()

    CACHE[cache_key] = answer

    return answer
# -----------------------
# Discord Events
# -----------------------

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    content = message.content.strip()

    # Ignore empty messages
    if not content:
        return

    # If using ! temporarily
    if content.startswith("!"):
        content = content[1:].strip()

    # Ignore messages that don't look like questions unless the bot is mentioned
    if (
        not content.startswith("!")
        and bot.user not in message.mentions
        and len(content.split()) < 2
    ):
        await bot.process_commands(message)
        return

    try:

        async with message.channel.typing():

            answer = ask_groq(content)

            if answer.strip() == "NOT_FOUND":

                await message.reply(
                    FALLBACK,
                    mention_author=False
                )

            else:

                await message.reply(
                    answer,
                    mention_author=False
                )

    except Exception as e:

        print(e)

        await message.reply(
            "⚠️ Sorry, something went wrong while checking the FAQ. Please try again.",
            mention_author=False
        )

    await bot.process_commands(message)


# -----------------------
# Start Bot
# -----------------------

bot.run(DISCORD_TOKEN)
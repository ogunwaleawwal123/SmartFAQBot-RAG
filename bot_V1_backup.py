import discord
from discord.ext import commands
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

with open("faq.txt", "r", encoding="utf-8") as f:
    FAQ_DATA = f.read()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

SYSTEM_PROMPT = f"""
You are DNA Funded's FAQ Assistant.

Your job:
- Answer ONLY from the FAQ information provided.
- Understand natural language questions.
- Understand spelling mistakes and slang.
- Be friendly and human.
- Match the member's tone and emotion.
- Use emojis naturally when appropriate.
- Give detailed answers when necessary.
- Never invent rules.
- Never guess.

If the answer exists in the FAQ knowledge, answer confidently.

If the answer does NOT exist in the FAQ knowledge, say:

"I'm not built to answer that yet. Please tag a moderator or contact DNA Funded Support for clarification 😊"

FAQ KNOWLEDGE:

{FAQ_DATA}
"""

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.content.startswith("!"):

        question = message.content[1:].strip()

        if not question:
            await message.channel.send(
                "Please type a question after the exclamation mark 😊"
            )
            return

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=0.3,
                max_tokens=700
            )

            answer = response.choices[0].message.content

            await message.channel.send(answer)

        except Exception as e:
            await message.channel.send(
                "Something went wrong while checking the FAQ. Please try again later."
            )
            print(e)

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
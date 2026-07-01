import time
import traceback
import importlib

import discord

from discord.ext import commands

from config import (
    DISCORD_TOKEN,
    MODERATOR_ROLE_IDS,
)

from llm import ask_groq

import cache
import retriever
import build_index

# ==========================================
# Intents
# ==========================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

START_TIME = time.time()

STATS = {
    "questions": 0,
    "fallbacks": 0,
    "errors": 0,
}

# ==========================================
# Fallback
# ==========================================

def build_fallback(guild):

    mentions = []

    for role_id in MODERATOR_ROLE_IDS:

        role = guild.get_role(role_id)

        if role:

            mentions.append(role.mention)

    if mentions:

        return (
            "I couldn't confidently find an answer based on the available information.\n\n"
            f'{" ".join(mentions)} help out with this please. Thanks 🙏'
        )

    return (
        "I couldn't confidently find an answer based on the available information.\n\n"
        "A moderator will help you shortly. 🙏"
    )

# ==========================================
# Ready
# ==========================================

@bot.event
async def on_ready():

    print("=" * 60)
    print(f"Logged in as {bot.user}")
    print("DNA Smart FAQ Bot Online")
    print("=" * 60)
# ==========================================
# Message Handler
# ==========================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.guild is None:
        return

    content = message.content.strip()

    if not content:
        return

    # --------------------------------------
    # Ignore command processing here
    # --------------------------------------

    if content.startswith("!"):
        await bot.process_commands(message)
        return

    # --------------------------------------
    # Ignore one-word messages
    # unless bot is mentioned
    # --------------------------------------

    mentioned = bot.user in message.mentions

    clean_content = content.replace(
        f"<@{bot.user.id}>",
        ""
    ).replace(
        f"<@!{bot.user.id}>",
        ""
    ).strip()

    if (
        not mentioned
        and len(clean_content.split()) < 2
    ):
        return

    try:

        STATS["questions"] += 1

        async with message.channel.typing():

            answer = ask_groq(
                message.author.id,
                clean_content
            )

        if answer == "NOT_FOUND":

            STATS["fallbacks"] += 1

            await message.reply(
                build_fallback(message.guild),
                mention_author=False
            )

        else:

            await message.reply(
                answer,
                mention_author=False
            )

    except Exception:

        STATS["errors"] += 1

        print("\n" + "=" * 60)
        traceback.print_exc()
        print("=" * 60 + "\n")

        await message.reply(
            "⚠️ Sorry, something went wrong while processing your question.",
            mention_author=False
        )

    await bot.process_commands(message)
    # ==========================================
# Admin Commands
# ==========================================

@bot.command(name="clearcache")
@commands.has_permissions(administrator=True)
async def clearcache(ctx):

    cache.clear()

    await ctx.reply(
        "✅ Cache cleared.",
        mention_author=False
    )


@bot.command(name="stats")
@commands.has_permissions(administrator=True)
async def stats(ctx):

    uptime = int(time.time() - START_TIME)

    hrs = uptime // 3600
    mins = (uptime % 3600) // 60
    secs = uptime % 60

    await ctx.reply(

        f"""
📊 **DNA FAQ Bot Stats**

Questions Answered : {STATS['questions']}
Fallbacks : {STATS['fallbacks']}
Errors : {STATS['errors']}
Cached Questions : {cache.size()}

Uptime :
{hrs}h {mins}m {secs}s
""",
        mention_author=False
    )


@bot.command(name="reloadfaq")
@commands.has_permissions(administrator=True)
async def reloadfaq(ctx):

    try:

        importlib.reload(build_index)
        importlib.reload(retriever)

        await ctx.reply(
            "✅ FAQ reloaded successfully.",
            mention_author=False
        )

    except Exception as e:

        await ctx.reply(
            f"❌ Reload failed.\n```{e}```",
            mention_author=False
        )


# ==========================================
# Error Handler
# ==========================================

@clearcache.error
@reloadfaq.error
@stats.error
async def admin_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.reply(
            "❌ You don't have permission to use this command.",
            mention_author=False
        )

    else:

        raise error


# ==========================================
# Run Bot
# ==========================================

bot.run(DISCORD_TOKEN)
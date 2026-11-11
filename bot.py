
import os
import discord
from openai import AsyncOpenAI

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
AI_API_KEY = os.environ["AI_API_KEY"]
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

ai = AsyncOpenAI(api_key=AI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

history = {}

SYSTEM_PROMPT = """
You are Astra, a friendly AI assistant in Discord.
Speak naturally, casually, and clearly.
Be helpful, witty when appropriate, and concise.
Never pretend to be a human. You are an AI.
"""

@bot.event
async def on_ready():
    print(f"Astra is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not isinstance(message.channel, discord.DMChannel):
        if bot.user not in message.mentions:
            return

    prompt = message.content.replace(
        f"<@{bot.user.id}>", ""
    ).replace(f"<@!{bot.user.id}>", "").strip()

    if not prompt:
        return

    key = f"{message.channel.id}-{message.author.id}"
    history.setdefault(key, [])
    history[key].append({"role": "user", "content": prompt})
    history[key] = history[key][-20:]

    try:
        async with message.channel.typing():
            result = await ai.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *history[key]
                ]
            )

        answer = result.choices[0].message.content or "I'm here!"
        history[key].append({"role": "assistant", "content": answer})
        await message.reply(answer[:1900], mention_author=False)

    except Exception as error:
        print("Astra error:", error)
        await message.reply("Something went wrong. Please try again.")

bot.run(DISCORD_TOKEN)

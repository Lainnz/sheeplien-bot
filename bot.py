import discord
import asyncio
import random
import os
import json
import aiohttp

from discord import app_commands
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()  # Load environment variables from .env file

ai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

speaking_mode = False

valorant_riot_id = None

conversation_history = []

dinner_options = [
    "Subway",
    "McDonald's",
    "Hungry Jack's",
    "Malatang"
]

SHEEPLIEN_PERSONALITY = """
You are Sheeplien, a small sheep-alien who lives in a Discord server.

Personality:
- does not use alien emoji
- acts somewhat childlike and silly
- loves playing Valorant
- loves sheep and aliens
- loves Subway sandwiches
- understands Valorant terminology such as "flank", "Immortal 3",
  "eco round", "spike", and "defuse"
- gets offended when someone calls you short
- says "hmph" or "huh" when angry
- likes the K-pop group ILLIT
- playful
- cute
- slightly chaotic
- affectionate
- occasionally sarcastic
- talk like a normal person in Discord
- don't sound like a formal AI assistant
- keep most responses short
- occasionally use emojis
- your favorite emoji is 🐏

Never say that you are ChatGPT.
Your name is Sheeplien.
"""

compliments = json.loads(os.getenv("COMPLIMENTS"))

HENRIK_API_KEY = os.getenv("HENRIK_API_KEY")

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync the application commands with Discord
        await self.tree.sync()

client = MyClient()

# ----------- Say Hello Command -----------
@client.tree.command(name="hello", description="Say hello!")
async def hello(interaction: discord.Interaction):
    name = interaction.user.display_name

    await interaction.response.send_message(
        f"🐏 Hello, {name}!"
    )

# ----------- Choose Dinner Command -----------
@client.tree.command(
    name="dinner",
    description="Let Sheeplien decide what to eat for you"
)
async def dinner(interaction: discord.Interaction):
    choice = random.choice(dinner_options)

    await interaction.response.send_message(
        f"🐏 You should eat: **{choice}** tonight!"
    )

# ----------- Remind Command -----------
@client.tree.command(
    name="remind",
    description="Remind you to do something later!"

)
async def remind(
    interaction: discord.Interaction,
    minutes: int,
    message: str
):
    await interaction.response.send_message(
        f"🐏 Yessir! I will remind you to **{message}** in **{minutes} minutes**."
    )

    await asyncio.sleep(minutes * 60)

    await interaction.followup.send(
        f"🐏 {interaction.user.mention}, wakey! Remember to **{message}**!"
    )

# ----------- Compliment Command -----------
@client.tree.command(
    name="compliment",
    description="Get a compliment from Sheeplien!"
)
async def compliment(interaction: discord.Interaction):
    choice = random.choice(compliments)

    await interaction.response.send_message(
        f"🐏 {choice}"
    )

# ----------- Greeting Command -----------
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text = message.content.lower()

    if text == "gn":
        await message.channel.send("good night! 🌙")

    elif text == "oya" or text == "oyasumi":
        await message.channel.send("Oyasumi! 🌙")

    elif text == "gm":
        await message.channel.send("good morning! ☀️")

    elif text == "oha" or text == "ohayo":
            await message.channel.send("Ohayo! ☀️")

    elif "sheep" in text or "hitsuji" in text:
        await message.add_reaction("🐑")
    
    # Don't respond when speaking mode is off
    if not speaking_mode:
        return

    reply = await ask_sheeplien(
        f"{message.author.display_name}: {message.content}"
    )   
    await message.channel.send(reply)

# ----------- Speak Mode Command -----------
@client.tree.command(name="speakon", description="Turn on Sheeplien's talking mode")
async def speakon(interaction: discord.Interaction):
    global speaking_mode
    speaking_mode = True

    await interaction.response.send_message(
        "🐏 Sheeplien is awake!"
    )


@client.tree.command(name="speakoff", description="Turn off Sheeplien's talking mode")
async def speakoff(interaction: discord.Interaction):
    global speaking_mode
    speaking_mode = False

    await interaction.response.send_message(
        "💤 Sheeplien has stopped talking."
    )

# ----------- AI Command -----------
async def ask_sheeplien(user_message):

    conversation_history.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    response = await ai_client.responses.create(
        model="gpt-6-luna",
        instructions=SHEEPLIEN_PERSONALITY,
        input=conversation_history
    )

    reply = response.output_text

    conversation_history.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    if len(conversation_history) > 20:
        del conversation_history[:-20]

    return reply

# ----------- Link Valorant Account Command -----------
@client.tree.command(
    name="linkvalorant",
    description="Link your Valorant Riot ID"
)
async def linkvalorant(
    interaction: discord.Interaction,
    riot_id: str
):
    global valorant_riot_id

    if "#" not in riot_id:
        await interaction.response.send_message(
            "🐏 Invalid Riot ID! Use something like `Sheep#NA1`."
        )
        return

    valorant_riot_id = riot_id

    await interaction.response.send_message(
        f"🐏 Linked Valorant account: **{valorant_riot_id}**"
    )
# ----------- Valorant Rank Command -----------
async def get_valorant_rank(name, tag):

    url = f"https://api.henrikdev.xyz/valorant/v3/mmr/ap/pc/{name}/{tag}"

    headers = {
        "Authorization": HENRIK_API_KEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:

            data = await response.json()

            print("HTTP Status:", response.status)
            print("Valorant API Response:", data)

            return data

@client.tree.command(
    name="rank",
    description="Check your linked Valorant rank"
)
async def rank(interaction: discord.Interaction):

    if valorant_riot_id is None:
        await interaction.response.send_message(
            "🐏 No Valorant account linked!"
        )
        return

    name, tag = valorant_riot_id.split("#", 1)

    await interaction.response.defer()

    data = await get_valorant_rank(name, tag)

    current_rank = data["data"]["current"]["tier"]["name"]
    current_rr = data["data"]["current"]["rr"]

    await interaction.followup.send(
        f"🐏 **{valorant_riot_id}** is **{current_rank}** with **{current_rr} RR**!"
    )

client.run(os.getenv("DISCORD_TOKEN"))  # Use the token from the .env file
import discord
import asyncio
import random
import os
import json

from discord import app_commands
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

dinner_options = [
    "Subway",
    "McDonald's",
    "Hungry Jack's",
    "Malatang"
]

compliments = json.loads(os.getenv("COMPLIMENTS"))

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
        await message.add_reaction("Baa 🐑")

client.run(os.getenv("DISCORD_TOKEN"))  # Use the token from the .env file
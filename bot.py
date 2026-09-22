import discord
import asyncio
import random
import os

from discord import app_commands
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
GUILD_ID = int(os.getenv("GUILD_ID"))  # Get the guild ID from the environment variable

dinner_options = [
    "Subway",
    "McDonald's",
    "Hungry Jack's",
    "Malatang"
]

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync the application commands with Discord
        guild = discord.Object(id=GUILD_ID)

        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)

        print(f"Synced {len(synced)} commands to test server:")
        for command in synced:
            print(f"- /{command.name}")

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

client.run(os.getenv("DISCORD_TOKEN"))  # Use the token from the .env file
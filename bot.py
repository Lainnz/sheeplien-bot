import discord
import os

from discord import app_commands
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync the application commands with Discord
        await self.tree.sync()

client = MyClient()

@client.tree.command(name="hello", description="Say hello!")
async def hello(interaction: discord.Interaction):
    name = interaction.user.display_name

    await interaction.response.send_message(
        f"Hello, {name}!"
    )

client.run(os.getenv("DISCORD_TOKEN"))  # Use the token from the .env file
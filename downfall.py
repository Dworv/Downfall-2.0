import discord, botconfig
from discord_slash import *
from discord_slash.model import *
from discord_slash.utils.manage_commands import *
from discord_slash.utils.manage_components import *
from discord.ext import tasks

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

@client.event
async def on_ready():
    print('Bot Online!')
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name="YouTube", url="https://www.youtube.com/watch?v=QtBDL8EiNZo", details="Apply today!"))

secret = botconfig.load_secret("C:/Users/Ryan/editing/Downfall_Editing_Bots/botconfig.toml", "new")
client.run(secret)
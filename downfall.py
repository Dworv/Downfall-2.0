import discord, botconfig
from discord_slash import *
from discord_slash.model import *
from discord_slash.utils.manage_commands import *
from discord_slash.utils.manage_components import *
from discord.ext import tasks

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

#start msg + client.vars
@client.event
async def on_ready():
    print('Bot Online!')
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name="YouTube", url="https://www.youtube.com/watch?v=QtBDL8EiNZo", details="Apply today!"))
    client.server = client.get_guild(848362097968283668)

    client.user_count_channel = client.server.get_channel(871150395932672020)
    client.member_count_channel = client.server.get_channel(871150597229936672)
    client.join_channel = client.server.get_channel(848567465281978399)

    client.user_role = client.server.get_role(849330016458113035)
    client.member_role = client.server.get_role(858942951980138496)

#embed generator slow
def sembed(main_text, sub_text, symbol):
    #symbol = symbol_library.get(symbol)
    embed = discord.Embed(discription=sub_text)
    embed.set_author(name=main_text)

#count updates
@tasks.loop(minutes=6)
async def count_update():
    await client.wait_until_ready
    user_count = len(client.server.members)
    member_count = len(client.member_role.members)
    await client.user_count_channel.edit(name=f"➝︱users: {user_count}")
    await client.member_count_channel.edit(name=f"➝︱members: {member_count}")
count_update.start

#welcome protocol
@client.event
async def on_member_join(member):
    embed = discord.Embed(description="Welcome to the official Downfall Editing server! We hope you have a great time and learn something new.")
    embed.set_author(name=f"Welcome, {member.name}", icon_url=member.avatar_url)
    await client.join_channel.send(embed=embed)
    await member.add_roles(client.user_role)

#secret
secret = botconfig.load_secret("C:/Users/Ryan/editing/Downfall_Editing_Bots/botconfig.toml", "new")
client.run(secret)
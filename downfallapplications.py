import discord
from discord_slash import *
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component

import sqlite3
import datetime
import botconfig

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)



#### for connecting ### -----------------------------------------------------

print("Bot Running...")

@client.event
async def on_connect():
    print('Bot Connected...')

@client.event
async def on_ready():
    print('Bot Ready!')
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name="YouTube", url="https://www.youtube.com/watch?v=QtBDL8EiNZo", details="Apply today!"))
    guild = client.get_guild(848362097968283668)

    app_guide_channel = client.get_channel(867873920551485450)
    app_review_channel = client.get_channel(867888747877629972)

    owner_role = discord.utils.get (guild.roles, id = 848379997119184916)
    downfall_role = guild.get_role(859301187106766878)
    reviewer_role = guild.get_role(848396601802096671)
    level_3_role = guild.get_role(848392622161657917)
    level_2_role = guild.get_role(848392734364794901)
    level_1_role = guild.get_role(848392980531380275)
    member_role = guild.get_role(858942951980138496)
    user_role = guild.get_role(849330016458113035)
    everyone_role = guild.get_role(848362097968283668)

con = sqlite3.connect("C:/Users/Ryan/editing/coding/applications_database_pbx.db")
c = con.cursor()
print("Database Online...")

### for connecting ^^^^ ### --------------------------------------------------

### quick variables ### ----------------------------------

guild = None

app_guide_channel = None
app_review_channel = None

owner_role = None
downfall_role = None
reviewer_role = None
level_3_role = None
level_2_role = None
level_1_role = None
member_role = None
user_role = None
everyone_role = None

owner_id = 848379997119184916
reviewer_id =848396601802096671
everyone_id = 848362097968283668

guild_ids = [848362097968283668]

### funtions! ### ----------------------------------------------------

def new_application_db_update(user, link):
    
    table_insert = ["faketicket", "fakeuser_id", "fakelink", "fakestatus", "fakedate"]
    c.execute("INSERT INTO applications_pbx VALUES (?,?,?,?,?)", table_insert)
    con.commit()


def new_application_inform_reviewers(user, link):
    print("reviewers informed...")

### commands! ### ----------------------------------------------------

@slash.slash(name="copy", description="Copies what you say!", permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(owner_id, SlashCommandPermissionType.ROLE, True)
                     ]}, guild_ids=guild_ids,
                     options=[
               create_option(
                 name="text",
                 description="Text to copy.",    
                 option_type=3,
                 required=True)])
async def copy(ctx, text: str):
    await ctx.send(text)

@slash.slash(name="apply", description=("APPLY TODAY YAAAAAAY"), 
                     permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(owner_id, SlashCommandPermissionType.ROLE, True)
                     ]}, guild_ids=guild_ids,
                     options=[
               create_option(
                 name="link",
                 description="Link to your application!",    
                 option_type=3,
                 required=True)])
async def copy(ctx, link):
    link_verify = new_application_db_update(ctx.author, link)
    if link_verify == False:
        return
    new_application_inform_reviewers(ctx.author, link)

    await ctx.send("Thanks for applying! We will get back to you as soon as we can.")

secret = botconfig.load_secret("botconfig.toml", "app")
client.run(secret)
import discord
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component
import threading
import time
from discord.ext import tasks
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType

print("Bot Running!")

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

guild_ids = [848362097968283668]

#for connecting 

@client.event
async def on_connect():
    print('Bot Connected!')

@client.event
async def on_ready():
    print('Bot Ready!')
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name="YouTube", url="https://www.youtube.com/watch?v=QtBDL8EiNZo", details="Here to help!"))

@client.event
async def on_member_join(member):
    print("Join")
    channel = client.get_channel(848567465281978399)
    await channel.send("Welcome "+member.mention+", have an awesome day!")
    role = discord.utils.get(member.guild.roles, id=849330016458113035)
    await member.add_roles(role)

@tasks.loop(minutes=10)
async def user_update_loop():
    await client.wait_until_ready()
    channel = client.get_channel(871150395932672020)
    user_count = len(channel.guild.members)
    await channel.edit(name=f"🔢︱users: {user_count}")
    
@tasks.loop(minutes=10)
async def member_update_loop():
    await client.wait_until_ready()
    channel = client.get_channel(871150597229936672)
    role = channel.guild.get_role(858942951980138496)
    member_count = len(role.members)
    await channel.edit(name=f"🔢︱members: {member_count}")

user_update_loop.start()
member_update_loop.start()  
  
@slash.slash(name="user_count", description="Displays the user count!", guild_ids=guild_ids)
async def user_count(ctx):
    member_count = len(ctx.guild.members)
    await ctx.send(f"There are {member_count} users in the server. That's pretty awesome!")

@slash.slash(name="copy", description="Copies what you say!", permissions={848362097968283668:
                     [
                     create_permission(849330016458113035, SlashCommandPermissionType.ROLE, False),
                     create_permission(848379997119184916, SlashCommandPermissionType.ROLE, True)
                     ]}, guild_ids=guild_ids,
                     options=[
               create_option(
                 name="text",
                 description="Text to copy.",    
                 option_type=3,
                 required=True)])
async def copy(ctx, text: str):
    await ctx.send(text)

@slash.slash(name="Announce",
             description="Command for announcing things", guild_ids=guild_ids,
             permissions={848362097968283668:
                     [
                     create_permission(849330016458113035, SlashCommandPermissionType.ROLE, False),
                     create_permission(848379997119184916, SlashCommandPermissionType.ROLE, True)
                     ]},
             options=[
               create_option(
                 name="channel",
                 description="Pick which channel to post this in.",    
                 option_type=3,
                 required=True,
                 choices=[
                  create_choice(
                    name="Featured",
                    value="f"
                  ),
                  create_choice(
                    name="News",
                    value="n"
                  ),
                  create_choice(
                    name="Rules",
                    value="r"
                  ),
                  create_choice(
                    name="Resources",
                    value="re"
                  )
                ]
               ),
               create_option(
                 name="content",
                 description="What would you like to say?",
                 option_type=3,
                 required=True,
               ),
               create_option(
                 name="embed",
                 description="Would you like the message to be in an embed?",
                 option_type=5,
                 required=True,
               )
             ])
             
async def Introduction(ctx, channel: str, content: str, embed: bool):
    if channel == "f":
        channelid = 848394255810297858
    elif channel == "n":
        channelid = 848626756746608670
    elif channel == "r":
        channelid = 848393658029047848
    elif channel == "re":
        channelid = 871105940861095987
    else:
        await ctx.send("Something went wrong in converting the channel placeholder value into a channel id.")
    
    await ctx.send(f"inputs were {channel},{content},{embed},{channelid}")
    destination = client.get_channel(channelid)
    if embed == False:
        await destination.send(content)
    if embed == True:
        embed = discord.Embed(
        description = content,
        color=discord.Color.dark_blue()
        )
        await destination.send(embed=embed)

@slash.slash(name="pfp", description="Displays your pfp!", guild_ids=guild_ids)
async def pfp(ctx): 
    embed = discord.Embed(
        title=f"Avatar of {ctx.author.display_name}",
        color=discord.Color.dark_blue()
    ).set_image(url=ctx.author.avatar_url)
    await ctx.send(embed=embed)
@slash.slash(name="resources", 
            description="Command to get resources",
            guild_ids=guild_ids)
async def resources(ctx):
    await ctx.send("Here are some resources for you.", components=[create_actionrow(
                                                                    create_button(style=ButtonStyle.URL, label="PASTEBIN", url="https://pastebin.com/yHsZ9b4g"),
                                                                    create_button(style=ButtonStyle.URL, label="RM-DISCORD", url="https://discord.gg/eZCqCe8qqe")
                                                                    ),
                                                                    create_actionrow(
                                                                    create_button(style=ButtonStyle.URL, label="SEUS-SHADER", url="https://drive.google.com/uc?export=download&id=1lJEDqfBG2qSEfACr6QR8PzGsNeigVs4-"),
                                                                    create_button(style=ButtonStyle.URL, label="SEUS-TXT", url="https://drive.google.com/uc?export=download&id=1OsQ54U5IwWYPgs8MU6geSdkcxMNruo9O"),
                                                                    create_button(style=ButtonStyle.URL, label="BSL-SHADER", url="https://drive.google.com/uc?export=download&id=1sBMhwvgtKCILAN1Zb8cT12tl4zIe5ZiG"),
                                                                    create_button(style=ButtonStyle.URL, label="BSL-TXT", url="https://drive.google.com/uc?export=download&id=10-6hydwpXa6xUhKzsAOh10fXjmO3f8oM")
                                                                    ),
                                                                    create_actionrow(
                                                                    create_button(style=ButtonStyle.URL, label="DOF-15", url="https://drive.google.com/uc?export=download&id=1Z8C-lPVQLXM2tf7TLc6qy5_KjI7RBRA9"),
                                                                    create_button(style=ButtonStyle.URL, label="DOF-35", url="https://drive.google.com/uc?export=download&id=1iMpx4dL949OYNjFSzbj6M5MyX7ZLzm5y"),
                                                                    create_button(style=ButtonStyle.URL, label="DOF-50", url="https://drive.google.com/uc?export=download&id=1fGlzJxtOZVGB3cU6U-yKXu2R7J2T7BKc"),
                                                                    create_button(style=ButtonStyle.URL, label="LUMA", url="https://drive.google.com/uc?export=download&id=1qEzFiUiRHTjDZuyv_WLEzEtDxQB8Eywx")
                                                                    ),
                                                                    create_actionrow(
                                                                    create_button(style=ButtonStyle.URL, label="SFX-PACK(g_bby)", url="https://drive.google.com/uc?export=download&id=1c_CUmODk69gc-dVtlexAGKu4BcbgV8pO"),
                                                                    create_button(style=ButtonStyle.URL, label="TL27-EDIT(allen)", url="https://discord.com/channels/549239954119852032/794306658067021835/863308187217166346"),
                                                                    create_button(style=ButtonStyle.URL, label="TIME-CHANGER", url="https://drive.google.com/uc?export=download&id=16z0zVJ4e-lhOZLPR6Vhx5USaZutKUePz"),
                                                                    create_button(style=ButtonStyle.URL, label="AE-EXPRESSION-SHAKE", url="https://drive.google.com/uc?export=download&id=1COCuV0hha1oAFG6e-Iyi7GtayRidvNOK")
                                                                    )
                                                                    ])

    

client.run("ODcwODE5NTUxMTI4OTg5NzU3.YQST6A.diZSReUkexw0cUVqjo1o_04IuMU")
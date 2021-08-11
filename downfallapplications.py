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
import validators

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

#### for connecting ### ----------------------------------------------###
### ------------------------------------------------------------------###
### ------------------------------------------------------------------###

con = sqlite3.connect("C:/Users/Ryan/editing/Downfall_Editing_Bots/applications_database_pbx.db")
c = con.cursor()
print("Database Online...")

print("Bot Running...")

@client.event
async def on_connect():
    print('Bot Connected...')

@client.event
async def on_ready():
    print('Bot Ready!')
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name="YouTube", url="https://www.youtube.com/watch?v=QtBDL8EiNZo", details="Apply today!"))
    global guild
    client.guild = client.get_guild(848362097968283668)
    client.app_guide_channel = client.get_channel(867873920551485450)
    client.app_review_channel = client.get_channel(867888747877629972)
    client.app_reviewing_channel = client.get_channel(867883406687469569)
    client.test_channel = client.get_channel(859178839127883797)
    client.owner_role = client.guild.get_role(848379997119184916)
    client.downfall_role = client.guild.get_role(859301187106766878)
    client.reviewer_role = client.guild.get_role(848396601802096671)
    client.level_3_role = client.guild.get_role(848392622161657917)
    client.level_2_role = client.guild.get_role(848392734364794901)
    client.level_1_role = client.guild.get_role(848392980531380275)
    client.member_role = client.guild.get_role(858942951980138496)
    client.user_role = client.guild.get_role(849330016458113035)
    client.everyone_role = client.guild.get_role(848362097968283668)

owner_id = 848379997119184916
reviewer_id = 848396601802096671
everyone_id = 848362097968283668

guild_ids = [848362097968283668]

### funtions! ### ----------------------------------------------------###
### ------------------------------------------------------------------###
### ------------------------------------------------------------------###

def basic_embed(text):
    embed = discord.Embed(description=text, colour=discord.Colour.purple())
    return embed

def review_report_embed(ticket, user, link, prerecs):
    text = f"Ticket: {ticket} \n User: {user} \n Link: {link} \n Pre-recs: {prerecs}"
    embed = discord.Embed(title="A new application has been submitted!",description=text, colour=discord.Colour.purple())
    return embed

def new_application_db_update(user, link, prerecs):
    
    valid=validators.url(link)
    if valid != True:
        return "invalid_link"

    c.execute("SELECT MAX(ticket) FROM applications_pbx")

    old_ticket = c.fetchall()
    old_ticket_int = int(old_ticket[0][0])
    ticket = old_ticket_int + 1

    user_id = user.id

    prerecs = int(prerecs)

    now = datetime.datetime.now()

    table_insert = [ticket, user_id, link, prerecs, "p", now]
    c.execute("INSERT INTO applications_pbx VALUES (?,?,?,?,?,?,NULL)", [table_insert[0],table_insert[1],table_insert[2],table_insert[3],table_insert[4],table_insert[5]])
    con.commit()

    return table_insert

async def new_application_inform_reviewers(info):
    ticket = info[0]
    user = client.get_user(info[1])
    link = info[2]
    prerecs = info[3]

    if prerecs == 1:
        prerecs = True
    else:
        prerecs = False

    embed = review_report_embed(ticket, user, link, prerecs)
    
    await client.app_reviewing_channel.send(embed=embed)

async def review_db_update(ticket, status):

    c.execute("SELECT * FROM applications_pbx WHERE ticket = (?)", [ticket])
    row = c.fetchall()

    if row == []:
      return "ticket_not_found"

    row = row[0]

    if row[4] != "p":
      return "not_pending"

    old_status = row[4]

    userid = row[1]
    user = client.get_user(userid)

    member = client.guild.get_member(userid)
    member_role = 0
    if client.level_1_role in member.roles:
      member_role=1
    if client.level_2_role in member.roles:
      member_role=2
    if client.level_3_role in member.roles:
      member_role=3

    if status != "d":
      int_status = int(status)
    
    if int_status <= member_role:
      return "incorrect_role"

    link = row[2]

    prerecs = False

    prerec_value = row[3]
    if prerec_value == "1":
      prerecs = True

    application_date_str = row[5]
    application_date = datetime.datetime.strptime(application_date_str, "%Y-%m-%d %H:%M:%S.%f")

    now = datetime.datetime.now()

    c.execute("UPDATE applications_pbx SET date2 = (?) WHERE ticket = (?)", [now, ticket])
    con.commit()
    c.execute("UPDATE applications_pbx SET status = (?) WHERE ticket = (?)", [status, ticket])
    con.commit()

    return [user, link, prerecs, old_status, application_date]

async def publish_review(ctx, ticket, status, overview, pros, procons, cons, app_info):
  
  applyer = app_info[0]
  applyer_mention = applyer.mention
  applyer_display = applyer.display_name

  reviewer = ctx.author
  reviewer_mention = reviewer.mention
  reviewer_display = reviewer.display_name

  link = app_info[1]

  colour = None
  imgur = None

  if status == "d":
    colour = 0xa3a1a5
    imgur = "https://i.imgur.com/JiNhix7.png"
  elif status == "1":
    colour = 0xa782df
    imgur = "https://i.imgur.com/IqGUuza.png"
  elif status == "2":
    colour = 0x6724cd
    imgur = "https://i.imgur.com/o8MxQ5x.png"
  elif status == "3":
    colour = 0x2f076c
    imgur = "https://i.imgur.com/l2taa6w.png"

  art_embed = discord.Embed(description=link, color=colour)
  art_embed.set_image(url=imgur)
  art_embed.set_author(name=f"Application by {applyer_display}", icon_url=applyer.avatar_url)
  overview_embed = discord.Embed(title="Overview", description=overview, color=colour)
  overview_embed.set_author(name=f"Review by {reviewer_display}", icon_url=reviewer.avatar_url)
  procons_embed = discord.Embed(title="Pros & Cons:", color=colour)
  procons_embed.add_field(name="***[ + ]***", value=pros.replace(", ","\n"), inline=True)
  procons_embed.add_field(name="***[+ / -]***", value=procons.replace(", ","\n"), inline=True)
  procons_embed.add_field(name="***[ - ]***", value=cons.replace(", ","\n"), inline=True)
  await client.review_channel.send("---------------------")
  await client.review_channel.send(embed=art_embed)
  await client.review_channel.send(embed=overview_embed)
  await client.review_channel.send(embed=procons_embed)

async def give_member_roles(user, status):

  member = client.guild.get_member(user.id)
  member_roles = 0

  if status == "d":
    return
  else:
    status = int(status)

  if status >= 1:
    await member.add_roles(client.level_1_role)
  if status >= 2:
    await member.add_roles(client.level_2_role)
  if status >= 3:
    await member.add_roles(client.level_3_role)

### commands! ### ----------------------------------------------------###
### ------------------------------------------------------------------###
### ------------------------------------------------------------------###

@slash.slash(name="Apply", description=("APPLY TODAY YAAAAAAY"), guild_ids=guild_ids,
                     options=[
               create_option(
                 name="link",
                 description="Link to your application!",    
                 option_type=3,
                 required=True),
               create_option(
                 name="prerecs",
                 description="Did you get your clips from someone else? Be honest, you can still get accepted.",    
                 option_type=3,
                 required=True,
                 choices=[
                  create_choice(
                    name="No",
                    value='0'),
                  create_choice(
                    name="Yes",
                    value='1')])
                    ])
async def copy(ctx, link, prerecs):
    update_return = new_application_db_update(ctx.author, link, prerecs)
    if update_return == "invalid_link":
        await ctx.send("Sorry, that appears to be an invalid link. Please make sure to copy it directly from your browser.")
        return

    await new_application_inform_reviewers(update_return)

    await ctx.send("Thanks for applying! We will get back to you as soon as we can.")

@slash.slash(name="Review",
             description="DEAL THEM PAIN", guild_ids=guild_ids,
             permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(reviewer_id, SlashCommandPermissionType.ROLE, True)
                     ]},
             options=[
               create_option(
                 name="ticket",
                 description="Enter the ticket on the application you would like to review",    
                 option_type=4,
                 required=True
               ),
               create_option(
                 name="status",
                 description="Make sure not to set it to something lower than they already are!",
                 option_type=3,
                 required=True,
                 choices=[
                  create_choice(
                    name="Reapp",
                    value='d'
                  ),
                  create_choice(
                    name="Level 1",
                    value='1'
                  ),
                  create_choice(
                    name="Level 2",
                    value='2'
                  ),
                  create_choice(
                    name="Level 3",
                    value='3'
                  )
                ]
               ),
               create_option(
                 name="overview",
                 description="Give an overview of your opinion of their edit. Be nice and Start off with a compliment!",
                 option_type=3,
                 required=True),
               create_option(
                 name="pros",
                 description="Seperate each with a comma with a space after it",
                 option_type=3,
                 required=True),
               create_option(
                 name="procons",
                 description="Seperate each with a comma with a space after it",
                 option_type=3,
                 required=True),
               create_option(
                 name="cons",
                 description="Seperate each with a comma with a space after it",
                 option_type=3,
                 required=True)
             ])
async def review(ctx, ticket, status, overview, pros, procons, cons):

    app_info = await review_db_update(ticket, status)

    if app_info == "ticket_not_found":
      embed = basic_embed("Sorry, we cannot find that ticket in the database. Make sure you are using the correct ticket.")
      await ctx.send(embed=embed)
      return

    if app_info == "not_pending":
      embed = basic_embed("Sorry, it appears that application has already been reviewed. Make sure you are using the correct ticket.")
      await ctx.send(embed=embed)
      return

    if app_info == "incorrect_role":
      embed = basic_embed("Sorry, it appears that you have attempted to give that user a role equal or smaller to what they already have. If you are trying to give a member the same level they already have, instead enter 'Reapp'.")
      await ctx.send(embed=embed)
      return

    await publish_review(ctx, ticket, status, overview, pros, procons, cons, app_info)

    user = app_info[0]

    await give_member_roles(user, status)

    embed = basic_embed(f"Ticket #{ticket} reviewed!")
    
    await ctx.send(embed=embed)

secret = botconfig.load_secret("botconfig.toml", "app")
client.run(secret)
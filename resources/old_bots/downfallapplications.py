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
from discord.ext import tasks


import sqlite3
import datetime
import botconfig
import validators
import calendar

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
    client.guild = client.get_guild(848362097968283668)
    client.app_guide_channel = client.get_channel(867873920551485450)
    client.app_review_channel = client.get_channel(867888747877629972)
    client.app_reviewing_channel = client.get_channel(867883406687469569)
    client.test_channel = client.get_channel(859178839127883797)
    client.roster_channel = client.get_channel(875141941728272444)
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
member_id = 858942951980138496
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

    int_status = 0

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
  await client.app_review_channel.send("---------------------")
  await client.app_review_channel.send(embed=art_embed)
  await client.app_review_channel.send(embed=overview_embed)
  await client.app_review_channel.send(embed=procons_embed)

async def give_member_roles(user, status):

  member = client.guild.get_member(user.id)
  member_roles = 0

  if status == "d":
    return "fail"
  else:
    status = int(status)

  if status >= 1:
    await member.add_roles(client.level_1_role)
  if status >= 2:
    await member.add_roles(client.level_2_role)
  if status >= 3:
    await member.add_roles(client.level_3_role)

async def full_reset_roster():

  c.execute('DELETE FROM roster_pbx;',);
  con.commit

  for member in client.member_role.members:
    userid = member.id
    level = 0
    if client.level_1_role in member.roles:
      level = 1
    if client.level_2_role in member.roles:
      level = 2
    if client.level_3_role in member.roles:
      level = 3
    if client.reviewer_role in member.roles:
      level = 4
    if client.owner_role in member.roles:
      level = 5
    name = member.name

    table_insert = [userid, level, name]
    c.execute("INSERT INTO roster_pbx VALUES (?,?,?,NULL,NULL)", [table_insert[0],table_insert[1],table_insert[2]])
    con.commit()

async def add_to_roster(user, status):
  userid = user.id
  status = int(status)
  level = 0
  if status == 1:
    level = 1
  if status == 2:
    level = 2
  if status == 3:
    level = 3
  if client.reviewer_role in user.roles:
    level = 4
  if client.owner_role in user.roles:
    level = 5
  name = user.name

  table_insert = [userid, level, name]
  c.execute("INSERT INTO roster_pbx VALUES (?,?,?,NULL,NULL)", [table_insert[0],table_insert[1],table_insert[2]])
  con.commit()

  await roster_update()

def change_birthday(user, date):

  userid = user.id

  datestr = f"{date[0]},{date[1]}"

  c.execute("UPDATE roster_pbx SET bday = (?) WHERE userid = (?)", [datestr, userid])
  con.commit()

async def roster_update():

  await client.roster_channel.purge()

  c.execute("SELECT * FROM roster_pbx WHERE rank = 5")
  Owner_list = c.fetchall()
  c.execute("SELECT * FROM roster_pbx WHERE rank = 4")
  Reviewer_list = c.fetchall()
  c.execute("SELECT * FROM roster_pbx WHERE rank = 3")
  Level_3_list = c.fetchall()
  c.execute("SELECT * FROM roster_pbx WHERE rank = 2")
  Level_2_list = c.fetchall()
  c.execute("SELECT * FROM roster_pbx WHERE rank = 1")
  Level_1_list = c.fetchall()

  formatted_list = f"▶️▶️▶️▶️▶️\n \n ***- R O S T E R -*** \n \n▶️▶️▶️▶️▶️\n\n\n"

  formatted_list = f"{formatted_list}***OWNER:*** \n \n"
  for owner in Owner_list:
    link = owner[3]
    if link == None:
      link = "Use /updatelink to add your youtube channel!"
    formatted_list = f"{formatted_list}**{owner[2]}** \n *Youtube:*  <{link}> \n"
  formatted_list = f"{formatted_list}\n ***REVIEWERS:*** \n \n"
  for reviewer in Reviewer_list:
    link = reviewer[3]
    if link == None:
      link = "Use /updatelink to add your youtube channel!"
    formatted_list = f"{formatted_list}**{reviewer[2]}** \n *Youtube:*  <{link}> \n"
  formatted_list = f"{formatted_list}\n ***LEVEL 3:*** \n \n"
  for level_3 in Level_3_list:
    link = level_3[3]
    if link == None:
      link = "Use /updatelink to add your youtube channel!"
    formatted_list = f"{formatted_list}**{level_3[2]}** \n *Youtube:*  <{link}> \n"
  formatted_list = f"{formatted_list}\n ***LEVEL 2:*** \n \n"
  for level_2 in Level_2_list:
    link = level_2[3]
    if link == None:
      link = "Use /updatelink to add your youtube channel!"
    formatted_list = f"{formatted_list}**{level_2[2]}** \n *Youtube:*  <{link}> \n"
  formatted_list = f"{formatted_list}\n ***LEVEL 1:*** \n \n"
  for level_1 in Level_1_list:
    link = level_1[3]
    if link == None:
      link = "Use /updatelink to add your youtube channel!"
    formatted_list = f"{formatted_list}**{level_1[2]}** \n *Youtube:*  <{link}> \n"
  formatted_list = f"{formatted_list} \n \n*schtoopid was here*"
  

  await client.roster_channel.send(formatted_list)

async def change_link(user, link):

  userid = user.id

  c.execute("UPDATE roster_pbx SET youtube = (?) WHERE userid = (?)", [link, userid])
  con.commit()

  await roster_update()

async def change_name(user, name):

  userid = user.id

  c.execute("UPDATE roster_pbx SET name = (?) WHERE userid = (?)", [name, userid])
  con.commit()

  await roster_update()

async def change_account(olduser, newuser):
  newuserid = newuser.id

  print(newuserid)

  #c.execute("UPDATE roster_pbx SET name = (?) WHERE userid = (?)", [name, userid])
  #con.commit()

  await roster_update()

### loops! ### -------------------------------------------------------###
### ------------------------------------------------------------------####
### ------------------------------------------------------------------###

### commands! ### ----------------------------------------------------###
### ------------------------------------------------------------------###
### ------------------------------------------------------------------###

@slash.slash(name="RosterAdmin", description="Roster Administrator Commands", permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(owner_id, SlashCommandPermissionType.ROLE, True)
                     ]}, guild_ids=guild_ids, options=[
               create_option(
                 name="command",
                 description="What would you like to do?",    
                 option_type=3,
                 required=True,
                 choices=[
                  create_choice(
                    name="Update",
                    value='update'),
                  create_choice(
                    name="Reset",
                    value='reset'),
                  create_choice(
                    name="UpdateAccount",
                    value="updateacc")]),
               create_option(
                 name="input",
                 description="What input are you inputting??",    
                 option_type=3,
                 required=False),
               create_option(
                 name="user",
                 description="Which profile do you want to edit",    
                 option_type=6,
                 required=False,
                 )])
async def rosteradmin(ctx, command, input=None, user=None):
  if command == "update":
    await roster_update()
    embed = basic_embed("The roster channel has been manually updated!")
    await ctx.send(embed=embed)
  elif command == "reset":
    await full_reset_roster()
    embed = basic_embed("The roster has been reset!")
    await ctx.send(embed=embed)
  elif command == "updateacc":
    await change_account(user, input)
    ctx.send("it worked sort of")
  else:
    embed = basic_embed("Sorry, it appears we are having trouble proccessing which command you picked. Please try again later.")
    await ctx.send(embed=embed)

#@slash.slash(name="ResetRoster", description="Resets the roster.", permissions={848362097968283668:
#                     [
#                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
#                     create_permission(owner_id, SlashCommandPermissionType.ROLE, True)
#                     ]}, guild_ids=guild_ids)
#async def reset_roster(ctx):
#  await full_reset_roster()
#  embed = basic_embed("The roster has been reset!")
#  await ctx.send(embed=embed)

#@slash.slash(name="UpdateRoster", description="Updates the roster channel.", permissions={848362097968283668:
#                     [
#                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
#                     create_permission(owner_id, SlashCommandPermissionType.ROLE, True)
#                     ]}, guild_ids=guild_ids)
#async def reset_roster(ctx):
#  await roster_update()
#  embed = basic_embed("The roster channel has been manually updated!")
#  await ctx.send(embed=embed)

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

    embed = basic_embed(f"Ticket #{ticket} reviewed!")
    await ctx.send(embed=embed)

    user = app_info[0]

    fail = await give_member_roles(user, status)

    if fail == "fail":
      return

    member = client.guild.get_member(user.id)

    await add_to_roster(member, status)

@slash.slash(name="UpdateBirthday", description="Updates birthday (Members only!)", permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(member_id, SlashCommandPermissionType.ROLE, True)
                     ]}, guild_ids=guild_ids,
                     options=[
               create_option(
                 name="month",
                 description="Which month is your birthday?",    
                 option_type=3,
                 required=True,
                 choices=[
                  create_choice(
                    name="January",
                    value='1'),
                  create_choice(
                    name="Febuary",
                    value='2'),
                  create_choice(
                    name="March",
                    value='3'),
                  create_choice(
                    name="April",
                    value='4'),
                  create_choice(
                    name="May",
                    value='5'),
                  create_choice(
                    name="June",
                    value='6'),
                  create_choice(
                    name="July",
                    value='7'),
                  create_choice(
                    name="August",
                    value='8'),
                  create_choice(
                    name="September",
                    value='9'),
                  create_choice(
                    name="October",
                    value='10'),
                  create_choice(
                    name="November",
                    value='11'),
                  create_choice(
                    name="December",
                    value='12'),
                 ]
                 ),
               create_option(
                 name="day",
                 description="Please just enter it right, ok?",    
                 option_type=4,
                 required=True)])
async def UpdateBirthday(ctx, month, day):
  
  month = int(month)

  days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  valid = None

  if 0 < day <= days[month]:
    valid = True
  else:
    valid = False

  if valid == False:
    await ctx.send("Sorry, it looks like you entered that date wrong. Please make sure you have the day correct.")
    return
  else:
    await ctx.send("Thanks for submitting your birthday!")

  date = [month, day]

  change_birthday(ctx.author, date)

@slash.slash(name="UpdateLink", description="Updates youtube link (Members only!)", permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(member_id, SlashCommandPermissionType.ROLE, True)
                     ]}, guild_ids=guild_ids,
                     options=[
               create_option(
                 name="link",
                 description="Link for your channel.",    
                 option_type=3,
                 required=True)])
async def UpdateLink(ctx, link):
  
  valid=validators.url(link)
  if valid != True:
    embed = basic_embed("Sorry, it appears your link is invalid.")
    await ctx.send(embed=embed)
    return
  else:
    await ctx.send("Thanks for submitting your youtube link!")

  await change_link(ctx.author, link)

@slash.slash(name="UpdateName", description="Updates your name in the database (Members only!)", permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(member_id, SlashCommandPermissionType.ROLE, True)
                     ]}, guild_ids=guild_ids,
                     options=[
               create_option(
                 name="name",
                 description="Name that will be stored in the database and displayed in the roster.",    
                 option_type=3,
                 required=True)])
async def UpdateName(ctx, name):
  
  embed = basic_embed("Thanks for updating your name!")
  await ctx.send(embed = embed)

  await change_name(ctx.author, name)

@slash.slash(name="Birthday", description="Find out what a member's birthday is.", guild_ids=guild_ids, permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(member_id, SlashCommandPermissionType.ROLE, True)
                     ]},options=[
                     create_option(
                 name="member",
                 description="Which member would you like to find the birthday of?",    
                 option_type=6,
                 required=True)])
async def birthday(ctx, member):

  valid = None
  if member in client.member_role.members:
    valid = True
  else:
    embed = basic_embed("Sorry, it appears you have selecter a user who is not part of the roster.")
    await ctx.send(embed=embed)
    return
  
  userid = member.id

  c.execute("SELECT * FROM roster_pbx WHERE userid = (?)", [userid])
  row = c.fetchall()
  row = row[0]  

  if row[4] == None:
    embed = basic_embed("Sorry, that user has not yet entered their birthday yet.")
    await ctx.send(embed=embed)
    return
 

  birthdaystring = row[4]
  birthdaylist = birthdaystring.split(",")
  month = int(birthdaylist[0])
  day = int(birthdaylist[1])

  monthstr = calendar.month_name[month]

  msg = f"{member.name}: {monthstr}, {day}"
  embed = basic_embed(msg)
  await ctx.send(embed = embed)

secret = botconfig.load_secret("C:/Users/Ryan/editing/Downfall_Editing_Bots/botconfig.toml", "app")
client.run(secret)
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
import asyncio
import sqlite3
import datetime
from profanityfilter import ProfanityFilter
import botconfig

con = sqlite3.connect("C:/Users/Ryan/editing/coding/muted_user_list_xgw.db")
c = con.cursor()

pf = ProfanityFilter()

print("Bot Running!")

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

guild_ids = [848362097968283668]

@client.event
async def on_connect():
    print('Bot Connected!')

spamcount = []

@client.event
async def on_ready():
    print('Bot Ready!')
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name="YouTube", url="https://www.youtube.com/watch?v=QtBDL8EiNZo", details="Stay safe!"))
    guild = client.get_guild(848362097968283668)
    for user in guild.members:
        spamcount.append([user.id,0,False])

#------------------------------------------------------------------------------------------------------------------#

owner_id = 848379997119184916
s_admin_id = 871208359527858277
i_admin_id = 848380092941205505
j_admin_id = 848392452029415434
user_id = 849330016458113035
vip_id = 850412206691450960
muted_id = 871211098257375292
everyone_id = 848362097968283668
member_id = 858942951980138496

rules = client.get_channel(848393658029047848)

#member_join stuff
@client.event
async def on_member_join(member):
    spamcount.append([member.id,0,False])
        
#on_message stuff
@client.event
async def on_message(message):
    guild = client.get_guild(848362097968283668)
    j_admin = discord.utils.get(guild.roles, id=j_admin_id)
    owner = discord.utils.get(guild.roles, id=owner_id)
    downfall = discord.utils.get(guild.roles, id=muted_id)
    
    check = pf.is_profane(message.content)

    if check == True:
        msg = await message.channel.send(f"Hey {message.author.mention}, watch your language!")
        await asyncio.sleep(5)
        await msg.delete() 
    
    # if j_admin in message.author.roles:
        # nope = 1
    # elif owner in message.author.roles:
        # nope = 1
    # elif downfall in message.author.roles:
        # nope = 1
    # else:
        # for entry in spamcount:
            # if entry[0] == message.author.id:
                # print("message sent")
                # msgcount = entry[1]
                # msgcount += 1
                # entry[1] = msgcount

            
#auto spam reset
# @tasks.loop(seconds=15)
# async def spam_reset():
    # await client.wait_until_ready()
    # guild = client.get_guild(848362097968283668)
    # bot_channel = guild.get_channel(873361195229413377)
    # for entry in spamcount:
        # userid = entry[0]
        # member = guild.get_member(userid)
        # if entry[1] < 8:
            # entry[1] = 0
        # elif entry[1] > 7 and entry[1] < 15:
            # if entry[2] == True:
                # entry[1] = 0
            # elif entry[2] == False:
                # await member.send(f"Hey you! Cool down! If you don't stop sending so many messages, I'll have to mute you!")
                # entry[2] = True
                # entry[1] -= 5
        # elif entry[1] > 14:
            # now = datetime.datetime.now()
            # mutetotaltime = datetime.timedelta(minutes = 1440)
            # releasedatetime = now + mutetotaltime
            
            # entry[1] = 0
            
            # c.execute("SELECT * FROM muted_users_list_xgw WHERE user = (?)", [userid])
            # fulltable = c.fetchall()
            # if len(fulltable) > 0:
                # return
            # table_insert = [userid, releasedatetime]
            # c.execute("INSERT INTO muted_users_list_xgw VALUES (?,?)", table_insert)
            # con.commit()
            
            # await member.add_roles(muted_role, reason=reason)
            # await member.remove_roles(user_role, reason=reason)
            # await bot_channel.send(f"{member.mention} was muted for 24 hours due to spamming.")

# spam_reset.start()

#warn command
@slash.slash(name="Warn",
             description="The Warning Command.", guild_ids=guild_ids,
             permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(j_admin_id, SlashCommandPermissionType.ROLE, True)
                     ]},
             options=[
               create_option(
                 name="user",
                 description="The prosecuted (i think thats how it works)",    
                 option_type=6,
                 required=True
               ),
               create_option(
                 name="reason",
                 description="You had better have a good one",
                 option_type=3,
                 required=True
               ),
               create_option(
                 name="clear",
                 description="This is optional; feel free to leave it empty",
                 option_type=5,
                 required=False,
             )])           
async def warn(ctx, user, reason, clear = None):
    userid = user.id
    user_role = ctx.guild.get_role(user_id)
    muted_role = ctx.guild.get_role(muted_id)
    member = discord.utils.get(ctx.guild.roles, id=member_id)
    j_admin = discord.utils.get(ctx.guild.roles, id=j_admin_id)
    i_admin = discord.utils.get(ctx.guild.roles, id=i_admin_id)
    s_admin = discord.utils.get(ctx.guild.roles, id=s_admin_id)
    owner = discord.utils.get(ctx.guild.roles, id=owner_id)
    guild = client.get_guild(848362097968283668)
    
    
    author_role = 0
    if j_admin in ctx.author.roles:
        author_role = 1
        if i_admin in ctx.author.roles:
            author_role = 2
            if s_admin in ctx.author.roles:
                author_role = 4
                if owner in ctx.author.roles:
                    author_role = 5
    
    user_role = 0
    if member in user.roles:
        user_role = 1
        if j_admin in user.roles:
            user_role = 2
            if i_admin in user.roles:
                user_role = 3
                if s_admin in user.roles:
                    user_role = 4
                    if owner in user.roles:
                        user_role = 5
                        
    
    if author_role < user_role:
        if clear == True:
            await ctx.send(f"You don't have permission to clear {user.mention}'s mutes!")
        else:
            await ctx.send(f"You do not have permission to warn {user.mention}")
        
    else:
        c.execute("SELECT * FROM warned_users_list_xgw WHERE user = (?)", [userid])
        row = c.fetchall()

        if clear == True:
            warn_check = len(row)
            if warn_check == 0:
                await ctx.send(f"{user.mention} has not been warned yet.")
                return
            c.execute("DELETE from warned_users_list_xgw WHERE user = (?)", [userid])
            con.commit()
            await ctx.send(f"You have cleared the mutes from {user.mention} for reason: `{reason}`.")
            return

        if row == []:
            table_insert = [userid, 1]
            c.execute("INSERT INTO warned_users_list_xgw VALUES (?,?)", table_insert)
            con.commit()
            await ctx.send(f"{user.mention} has been warned for: `{reason}`. This their first warning.")
            return
        
        row1 = row[0][1]
        
        warn_count = int(row1)
        
        new_warn_count = warn_count + 1
        good_warn_count = int(new_warn_count)
        c.execute("UPDATE warned_users_list_xgw SET warns = (?) WHERE user = (?)", [good_warn_count, userid])
        con.commit()
        await ctx.send(f"{user.mention} has been warned for reason: `{reason}`. This is warn #{new_warn_count}")

#warnlist command
@slash.slash(name="Warnlist", description="Displays all warned users!", guild_ids=guild_ids)
async def warned_list(ctx):
    c.execute("SELECT * FROM warned_users_list_xgw")
    warnedlist = c.fetchall()
    warnedliststring = "List of muted users:"+"\n"
    if warnedlist == []:
        await ctx.send("Sorry, it appears no warned users have been detected in the database.")
        return
    for row in warnedlist:
        getuser = discord.utils.get(ctx.guild.members, id=row[0])
        warn_count = row[1]
        userdisplayname = getuser.display_name
        warnedliststring = f"{warnedliststring}\n Name: {userdisplayname} | # of warns: {warn_count}"
    await ctx.send(warnedliststring)

#mute command
@slash.slash(name="Mute",
             description="The Very Epic Mute Command.", guild_ids=guild_ids,
             permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(j_admin_id, SlashCommandPermissionType.ROLE, True)
                     ]},
             options=[
               create_option(
                 name="user",
                 description="Target of the mute laser gun. *pew, pew*",    
                 option_type=6,
                 required=True
               ),
               create_option(
                 name="length",
                 description="How long will the user stay muted? Choose wisely (Based off of your protocols)!",
                 option_type=3,
                 required=True,
                 choices=[
                  create_choice(
                    name="5 minutes",
                    value='5'
                  ),
                  create_choice(
                    name="30 minutes",
                    value='30'
                  ),
                  create_choice(
                    name="2 hours",
                    value='120'
                  ),
                  create_choice(
                    name="6 hours",
                    value='360'
                  ),
                  create_choice(
                  name="24 hours",
                  value='1440')
                ]
               ),
               create_option(
                 name="reason",
                 description="You had better have a good one",
                 option_type=3,
                 required=True
               )
             ])           
async def mute(ctx, user, length: str, reason):
    user_role = ctx.guild.get_role(user_id)
    muted_role = ctx.guild.get_role(muted_id)
    member = discord.utils.get(ctx.guild.roles, id=member_id)
    j_admin = discord.utils.get(ctx.guild.roles, id=j_admin_id)
    i_admin = discord.utils.get(ctx.guild.roles, id=i_admin_id)
    s_admin = discord.utils.get(ctx.guild.roles, id=s_admin_id)
    owner = discord.utils.get(ctx.guild.roles, id=owner_id)
    guild = client.get_guild(848362097968283668)
    
    
    author_role = 0
    if j_admin in ctx.author.roles:
        author_role = 1
        if i_admin in ctx.author.roles:
            author_role = 2
            if s_admin in ctx.author.roles:
                author_role = 4
                if owner in ctx.author.roles:
                    author_role = 5
    
    user_role = 0
    if member in user.roles:
        user_role = 1
        if j_admin in user.roles:
            user_role = 2
            if i_admin in user.roles:
                user_role = 3
                if s_admin in user.roles:
                    user_role = 4
                    if owner in user.roles:
                        user_role = 5
                        
    intlength = int(length)
    if intlength > 59:
        length_legible = f'{intlength / 60} hours'
    else:
        length_legible = f'{intlength} minutes'
    
    if author_role < user_role:
        await ctx.send(f"You do not have permission to mute {user.mention}")
    else:
        now = datetime.datetime.now()
        mutetotaltime = datetime.timedelta(minutes = intlength)
        releasedatetime = now + mutetotaltime
        
        muted_user_id = user.id
        c.execute("SELECT * FROM muted_users_list_xgw WHERE user = (?)", [muted_user_id])
        fulltable = c.fetchall()
        if len(fulltable) > 0:
            await ctx.send(f"Sorry, it appears {user} has already been muted. Please try again later.")
            return
            
        await ctx.send(f"{ctx.author.mention} has muted {user.mention} for {length_legible} because of reason: `{reason}`. ")    
        table_insert = [muted_user_id, releasedatetime]
        c.execute("INSERT INTO muted_users_list_xgw VALUES (?,?)", table_insert)
        con.commit()
        guild = client.get_guild(848362097968283668)
        user_role = guild.get_role(user_id)
        muted_role = guild.get_role(muted_id)
        await user.add_roles(muted_role, reason=reason)
        await user.remove_roles(user_role, reason=reason)
 
#auto unmute check 
@tasks.loop(seconds=10)
async def user_unmute_check():
    await client.wait_until_ready()
    c.execute("SELECT * FROM muted_users_list_xgw")
    mutelist = c.fetchall()
    for muted_user in mutelist:
        userid = muted_user[0]
        releasedt = muted_user[1]
        release_formatted = datetime.datetime.strptime(releasedt, "%Y-%m-%d %H:%M:%S.%f")
        if release_formatted < datetime.datetime.now():
            guild = client.get_guild(848362097968283668)
            user_role = guild.get_role(user_id)
            muted_role = guild.get_role(muted_id)
            unmute_user = guild.get_member(userid)
            await unmute_user.remove_roles(muted_role, reason="Automatic Unmute")
            await unmute_user.add_roles(user_role, reason="Automatic Unmute")
            c.execute("DELETE from muted_users_list_xgw WHERE user = (?)", [userid])
            con.commit()
            print(f"Successfully removed {userid} from the muted list.")

user_unmute_check.start()

#mutelist command
@slash.slash(name="Mutelist", description="Displays all muted users!", guild_ids=guild_ids)
async def mutelist(ctx):
    c.execute("SELECT * FROM muted_users_list_xgw")
    mutedlist = c.fetchall()
    mutedliststring = "List of muted users:"+"\n"
    if mutedlist == []:
        await ctx.send("Sorry, it appears no muted users have been detected in the database.")
        return
    for row in mutedlist:
        getuser = discord.utils.get(ctx.guild.members, id=row[0])
        release_format = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f")
        time_until_unmute = release_format - datetime.datetime.now()
        # time_until_unmute_formatted = datetime.datetime.strftime(time_until_unmute, "%H:%M:%S")
        userdisplayname = getuser.display_name
        mutedliststring = f"{mutedliststring}\n Name: {userdisplayname} | Time until unmute: {time_until_unmute}"
    await ctx.send(mutedliststring)

#unmute command
@slash.slash(name="Unmute",
             description="The command to use after they beg for forgiveness.", guild_ids=guild_ids,
             permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(j_admin_id, SlashCommandPermissionType.ROLE, True)
                     ]},
             options=[
               create_option(
                 name="user",
                 description="The sad and alone muted user",    
                 option_type=6,
                 required=True
               ),
               create_option(
                 name="reason",
                 description="Why are you undoing this mute???????????",    
                 option_type=3,
                 required=True
               )
               ])
async def unmute(ctx, user, reason):
    user_role = ctx.guild.get_role(user_id)
    muted_role = ctx.guild.get_role(muted_id)
    muted = ctx.guild.get_role(muted_id)
    userid = user.id
    member = discord.utils.get(ctx.guild.roles, id=member_id)
    j_admin = discord.utils.get(ctx.guild.roles, id=j_admin_id)
    i_admin = discord.utils.get(ctx.guild.roles, id=i_admin_id)
    s_admin = discord.utils.get(ctx.guild.roles, id=s_admin_id)
    owner = discord.utils.get(ctx.guild.roles, id=owner_id)
    guild = client.get_guild(848362097968283668)
    
    author_role = 0
    if i_admin in ctx.author.roles:
        author_role = 1
        if s_admin in ctx.author.roles:
            author_role = 4
            if owner in ctx.author.roles:
                author_role = 5
    
    user_role = 0
    if member in user.roles:
        user_role = 1
        if j_admin in user.roles:
            user_role = 2
            if i_admin in user.roles:
                user_role = 3
                if s_admin in user.roles:
                    user_role = 4
                    if owner in user.roles:
                        user_role = 5
                        
    if author_role < user_role:
        await ctx.send(f"You do not have permission to unmute {user.mention}")
    else:    
        if muted in user.roles:
            user_role = guild.get_role(user_id)
            muted_role = guild.get_role(user_id)
            await user.remove_roles(muted_role, reason=reason)
            await user.add_roles(user_role, reason=reason)
            c.execute("DELETE from muted_users_list_xgw WHERE user = (?)", [userid])
            con.commit()
            await ctx.send(f"{user.mention} has been unmuted.")
        else:
            await ctx.send(f"{user.mention} is not muted.")

#ban command
@slash.slash(name="Ban",
             description="When they give you no other choice", guild_ids=guild_ids,
             permissions={848362097968283668:
                     [
                     create_permission(everyone_id, SlashCommandPermissionType.ROLE, False),
                     create_permission(i_admin_id, SlashCommandPermissionType.ROLE, True)
                     ]},
             options=[
               create_option(
                 name="user",
                 description="The defendant",    
                 option_type=6,
                 required=True
               ),
               create_option(
                 name="reason",
                 description="....",    
                 option_type=3,
                 required=True
               )
               ])
async def ban(ctx, user, reason):
    muted = discord.utils.get(ctx.guild.roles, id=muted_id)
    member = discord.utils.get(ctx.guild.roles, id=member_id)
    j_admin = discord.utils.get(ctx.guild.roles, id=j_admin_id)
    i_admin = discord.utils.get(ctx.guild.roles, id=i_admin_id)
    s_admin = discord.utils.get(ctx.guild.roles, id=s_admin_id)
    owner = discord.utils.get(ctx.guild.roles, id=owner_id)
    guild = client.get_guild(848362097968283668)
    
    author_role = 0
    if i_admin in ctx.author.roles:
        author_role = 1
        if s_admin in ctx.author.roles:
            author_role = 4
            if owner in ctx.author.roles:
                author_role = 5
    
    user_role = 0
    if member in user.roles:
        user_role = 1
        if j_admin in user.roles:
            user_role = 2
            if i_admin in user.roles:
                user_role = 3
                if s_admin in user.roles:
                    user_role = 4
                    if owner in user.roles:
                        user_role = 5
                        
    if author_role <= user_role:
        await ctx.send(f"You do not have permission to ban {user.mention}")
    else:
        await user.ban(reason=reason, delete_message_days=0)
        await ctx.send(f"You have successfully banned {user.mention}, for reason: `{reason}`")
    


secret = botconfig.load_secret("botconfig.toml", "mod")
client.run(secret)
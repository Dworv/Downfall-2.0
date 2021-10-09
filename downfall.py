
#todo:
#add func for fails and successes

from asyncio.windows_events import SelectorEventLoop
import discord, botconfig, sqlite3, validators
from discord_slash import *
from discord_slash.model import *
from discord_slash.utils.manage_commands import *
from discord_slash.utils.manage_components import *
from discord.ext import tasks

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
con = sqlite3.connect("C:/Users/Ryan/editing/Downfall_Editing_Bots/downfall.db")
c = con.cursor()

guild_ids = [848362097968283668]

#embed generators
def sembed(main_text, sub_text, symbol):
    #symbol = symbol_library.get(symbol)
    embed = discord.Embed(description=sub_text)
    embed.set_author(name=main_text)
    return embed
async def qembed(main_text, sub_text, symbol, ctx):
    #symbol = symbol_library.get(symbol)
    embed = discord.Embed(description=sub_text)
    embed.set_author(name=main_text)
    return await ctx.send(embed = embed)

async def regenerate_roster_embeds():
    await client.roster_channel.purge()
    embedList = []
    levelDicts = [
                    None,
                    {
                        "title":"Level 1",
                        "desc":"Level 1 Members",
                        "color":0xaf78f8
                    },
                    {
                        "title":"Level 2",
                        "desc":"Level 2 Members",
                        "color":0x901ae4
                    },
                    {
                        "title":"Level 3",
                        "desc":"Level 3 Members",
                        "color":0x540072
                    },
                    {
                        "title":"Reviewers",
                        "desc":"The Reviewers",
                        "color":0x5d00cf
                    },
                    {
                        "title":"Owner",
                        "desc":"The Owner",
                        "color":0x240020
                    },
                ]
    for level in range(1,6):
        c.execute("SELECT * FROM roster WHERE rank = (?)", [level])
        rawList = c.fetchall()
        levelDict = levelDicts[level]
        embed = discord.Embed(title=levelDict["title"], description=levelDict["desc"], color=levelDict["color"])
        for memberId, rank, customName, youtube, bDay in rawList:
            member = client.get_user(int(memberId))
            if customName != None:
                name = customName
            else:
                name = member.name
            embed.add_field(name=name, value=f"Youtube: {youtube}", inline = False)
        embedList.append(embed)
    return await client.roster_channel.send(embed=embedList[4]), await client.roster_channel.send(embed=embedList[3]), await client.roster_channel.send(embed=embedList[2]), await client.roster_channel.send(embed=embedList[1]), await client.roster_channel.send(embed=embedList[0])

#start msg + client.vars
@client.event
async def on_ready():
    print('Bot Online!')
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name="YouTube", url="https://www.youtube.com/watch?v=QtBDL8EiNZo", details="Apply today!"))
    client.server = client.get_guild(848362097968283668)

    client.user_count_channel = client.server.get_channel(871150395932672020)
    client.member_count_channel = client.server.get_channel(871150597229936672)
    client.join_channel = client.server.get_channel(848567465281978399)
    client.review_channel = client.server.get_channel(867888747877629972)
    client.reviewing_channel = client.server.get_channel(867883406687469569)
    client.staff_chat_channel = client.server.get_channel(848393658029047849)
    client.roster_channel = client.server.get_channel(896267571278536756)

    client.owner_role = client.server.get_role(848379997119184916)
    client.user_role = client.server.get_role(849330016458113035)
    client.member_role = client.server.get_role(858942951980138496)
    client.level_1_role = client.server.get_role(848392980531380275)
    client.level_2_role = client.server.get_role(848392734364794901)
    client.level_3_role = client.server.get_role(848392622161657917)
    client.oitc_role = client.server.get_role(895185551429369877)
    client.fan_role = client.server.get_role(895185993450287144)
    client.minor_ping_role = client.server.get_role(895185993450287144)

    
    await regenerate_roster_embeds()

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

#resource embed generator
def generate_resource_embed(type: int):
    type = int(type)
    c.execute("SELECT * FROM resources WHERE Type = (?)", [type])
    
    listRaw = c.fetchall()
    listFormatted = ""
    nameList = ["Software", "Shaders", "Resource Packs", "Plugins", "Sound Effects"]
    if listRaw == []:
        embed = discord.Embed(title = nameList[type], description = "`No resources availible.`")
    for resource in listRaw:
        listFormatted = f"{listFormatted}\n\n**[{resource[0]}]({resource[2]})**\n`Date Added: {resource[3]}, Author Id: {resource[4]}`"
    embed = discord.Embed(title = nameList[type], description = listFormatted)
    return embed

def generate_help_components():
    c.execute("SELECT * FROM resources")
    commandCount = len(c.fetchall())
    pageCount = commandCount//4
    optionList = []
    for page in range(1, pageCount+1):
        optionList.append(create_select_option(f"Page {page}", str(page)))
    return optionList

def generate_help_embed(page: int):
    page = int(page)
    c.execute("SELECT * FROM commands")
    raw_page = page
    listRaw = c.fetchall()
    listFilter = []
    if page == 1:
        page = 0
    else:
        page = (page-1)*4
    for rawPage in range(page, page+4):
        try:
            listFilter.append(listRaw[rawPage])
        except:
            pass
    embedDescription = ""
    for name,description in listFilter:
        embedDescription = f"{embedDescription}\n\n**{name}**\n`{description}`"

    return discord.Embed(title = f"Page: {raw_page}", description = embedDescription)

def generate_role_content():
    embed = discord.Embed(title="Roles", description="GET YOUR ROLES HERE!!!!")
    buttons = []
    role_list = [
                    {
                        "name": "OITC Troop",
                        "desc": "All the people that want to get pinged for OITC.",
                        "id": 895185551429369877,
                        "cid": "6901",
                        "color": ButtonStyle.red
                    },
                    {
                        "name": "Downfall Fans",
                        "desc": "Epic role take it its free.",
                        "id": 895185993450287144,
                        "cid": "6902",
                        "color": ButtonStyle.blue
                    },
                    {
                        "name": "Minor Pings",
                        "desc": "You will be pinged exessively. DO IT.",
                        "id": 895185993450287144,
                        "cid": "6903",
                        "color": ButtonStyle.green
                    },
                ]
    for role in role_list:
        embed.add_field(name=role["name"], value=role["desc"], inline = False)
        buttons.append(create_button(role["color"], role["name"], custom_id=role["cid"]))
    [create_actionrow(buttons[0],buttons[1],buttons[2])]
    return [embed,[create_actionrow(buttons[0],buttons[1],buttons[2])]]

##################################### --- commands --- ############################################

#subcommand builder
def build_command(verb, level_1 = None, level_2 = None, level_3 = None):
    if level_1 != None:
        desc = level_1[0]
        fn = level_1[1]
        slash.slash(name="profile", description="sample", guild_ids=guild_ids)(fn)
    if level_2 != None:
        for (subcommand, description, fn, input) in level_2:
            if input == None:
                slash.subcommand(base=verb, name=subcommand, description=description, guild_ids=guild_ids)(fn)
            elif input[0] != 0:
                #1: String; 2: Integer; 3: Boolean; 4: User; 5: Channel; 6: Role
                optype = input[0] + 2
                slash.subcommand(base=verb, name=subcommand, description=description, guild_ids=guild_ids, options = [create_option(name=input[1],description=input[2],option_type=optype,required=input[3])])(fn)
            elif input[0] == 0:
                choices = []
                for (title,value) in input[4]:
                    choices.append(create_choice(name=title,value=value))
                slash.subcommand(base=verb, name=subcommand, description=description, guild_ids=guild_ids, options = [create_option(name=input[1],description=input[2],option_type=3,required=input[3],choices=choices)])(fn)
    if level_3 != None:
        for (subgroup, name, description, fn, input) in level_3:
            if input == None:
                slash.subcommand(base=verb, subcommand_group=subgroup, name=name, description=description, guild_ids=guild_ids)(fn)
            elif input[0] != 0:
                #1: String; 2: Integer; 3: Boolean; 4: User; 5: Channel; 6: Role
                optype = input[0] + 2
                slash.subcommand(base=verb, name=name, subcommand_group=subgroup, description=description, guild_ids=guild_ids, options = [create_option(name=input[1],description=input[2],option_type=optype,required=input[3])])(fn)
            elif input[0] == 0:
                choices = []
                for (title,value) in input[4]:
                    choices.append(create_choice(name=title,value=value))
                slash.subcommand(base=verb, name=name, subcommand_group=subgroup, description=description, guild_ids=guild_ids, options = [create_option(name=input[1],description=input[2],option_type=3,required=input[3],choices=choices)])(fn)

#passive menu component detect
@client.event
async def on_component(ctx: ComponentContext):
    if ctx.custom_id == "12345":
        await ctx.edit_origin(embed = generate_help_embed(int(ctx.selected_options[0])))
    elif ctx.custom_id == "12346":
        await ctx.edit_origin(embed=generate_resource_embed(int(ctx.selected_options[0])))
    elif ctx.custom_id == "6901":
        if client.oitc_role not in ctx.author.roles:
            await ctx.author.add_roles(client.oitc_role)
            embed = sembed("Role Added", "You have been granted the OITC Troop role!", "success")
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.author.remove_roles(client.oitc_role)
            embed = sembed("Role Removed", "You have been stripped of the OITC Troop role.", "success")
            await ctx.send(embed=embed, hidden=True)
    elif ctx.custom_id == "6902":
        if client.fan_role not in ctx.author.roles:
            await ctx.author.add_roles(client.fan_role)
            embed = sembed("Role Added", "You have been granted the Downfall Fan role!", "success")
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.author.remove_roles(client.fan_role)
            embed = sembed("Role Removed", "You have been stripped of the Downfall Fan role. I guess you aren't a fan anymore?", "success")
            await ctx.send(embed=embed, hidden=True)
    elif ctx.custom_id == "6903":
        if client.minor_ping_role not in ctx.author.roles:
            await ctx.author.add_roles(client.minor_ping_role)
            embed = sembed("Role Added", "You have been granted the Minor Pings role!", "success")
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.author.remove_roles(client.minor_ping_role)
            embed = sembed("Role Removed", "You have been stripped of the Minor Pings role. The pain is over.", "success")
            await ctx.send(embed=embed, hidden=True)

#new-help command
@slash.subcommand(base="new", name="command", description="A command to add a command to the help menu.", guild_ids=guild_ids, options=[
            create_option(name="name", description="What will the new resource be called?", option_type=3,required=True),
            create_option(name="description", description="The description of the command.", option_type=3,required=True)
            ])
async def new_help(ctx, name, description):
    if client.owner_role not in ctx.author.roles:
        await qembed("Interaction Failed", "You do not have clearance to utilize this command.", "fail", ctx)
        return
    c.execute(f"SELECT * FROM commands WHERE Name = (?)", [name])
    if c.fetchall() != []:
        await qembed("Interaction Failed", "It appears that name has already been taken.", "fail", ctx)
        return
    c.execute("INSERT INTO commands VALUES (?,?)", [name, description])
    con.commit()
    await qembed("Command added successfully", f"Name: `{name}`, Description: `{description}`", "success", ctx)

#remove-help command
@slash.subcommand(base="remove", name="command", description="*Bruh moment*", 
                    guild_ids=guild_ids, options=[create_option(name="name", description="The name of the target.", option_type=3,required=True)])
async def remove_command(ctx, name):
    if client.owner_role not in ctx.author.roles:
        await qembed("Interaction Failed", "You do not have clearance to utilize this command.", "fail", ctx)
        return
    c.execute(f"SELECT * FROM commands WHERE Name = (?)", [name])
    if c.fetchall() == []:
        await qembed("Interaction Failed", "It appears a command with that name does not exist.", "fail", ctx)
        return
    c.execute("DELETE FROM commands WHERE Name = (?)", [name])
    con.commit()
    await qembed("Command removed successfully", f"Command with Name: `{name}` has been removed from the help menu.", "success", ctx)

#help command
@slash.slash(name="help", description="A very helpful command...", guild_ids=guild_ids)
async def help(ctx):
    embed = generate_help_embed(1)
    await ctx.send(embed=embed, components=[create_actionrow(
            create_select(
                options = generate_help_components(),
                placeholder="Page:", 
                min_values=0, 
                max_values=1, 
                custom_id=12345
                ))])

#new-resourse command
@slash.subcommand(base="new", name="resource", description="A command to make a new resource.", guild_ids=guild_ids, options=[
            create_option(name="name", description="What will the new resource be called?", option_type=3,required=True),
            create_option(name="link", description="The link to the resource", option_type=3,required=True),
            create_option(name="type", description="What section shall the resource be placed in?", option_type=4,required=True)
            ])
async def new_resource(ctx,name,link,type):
    if client.owner_role not in ctx.author.roles:
        await qembed("Interaction Failed", "You do not have clearance to utilize this command.", "fail", ctx)
        return
    if not validators.url(link): 
        await qembed("Interaction Failed", "Invalid link submitted.", "fail", ctx)
        return
    if type < 0 or type > 4:
        await qembed("Interaction Failed", "Type out of bounds.", "fail", ctx)
        return
    c.execute(f"SELECT * FROM resources WHERE Name = (?)", [name])
    if c.fetchall() != []:
        await qembed("Interaction Failed", "It appears that name has already been taken.", "fail", ctx)
        return
    c.execute(f"SELECT * FROM resources WHERE Link = (?)", [link])
    if c.fetchall() != []:
        await qembed("Interaction Failed", "It appears that link has already been taken.", "fail", ctx)
        return
    date = datetime.datetime.now().strftime("%y/%m/%d")
    c.execute("INSERT INTO resources VALUES (?,?,?,?,?)", [name, type, link, str(date), ctx.author.id])
    con.commit()
    await qembed("Resource added successfully", f"Name: `{name}`, Link: `{link}`", "success", ctx)

#remove-resource command
@slash.subcommand(base="remove", name="resource", description="For when you screw up enough that this is nessicary...", 
                    guild_ids=guild_ids, options=[create_option(name="name", description="The name of the target.", option_type=3,required=True)])
async def remove_resource(ctx, name):
    if client.owner_role not in ctx.author.roles:
        await qembed("Interaction Failed", "You do not have clearance to utilize this command.", "fail", ctx)
        return
    c.execute(f"SELECT * FROM resources WHERE Name = (?)", [name])
    if c.fetchall() == []:
        await qembed("Interaction Failed", "It appears a resource with that name does not exist.", "fail", ctx)
        return
    c.execute("DELETE FROM resources WHERE Name = (?)", [name])
    con.commit()
    await qembed("Resource removed successfully", f"Resource with Name: `{name}` has been removed from the database.", "success", ctx)

#resource command
@slash.slash(name="resources", description="A command for all of your editing resources.", guild_ids=guild_ids)
async def resources(ctx):
    embed = generate_resource_embed(0)
    select = create_select(
        options=[
        create_select_option("Software", value="0", emoji="1️⃣"),
        create_select_option("Shaders", value="1", emoji="2️⃣"),
        create_select_option("Resource Packs", value="2", emoji="3️⃣"),
        create_select_option("Plugins", value="3", emoji="4️⃣"),
        create_select_option("Sound Effects", value="4", emoji="5️⃣"),
        ], placeholder="Type:", min_values=0, max_values=1, custom_id=12346
        )
    await ctx.send(embed=embed, components=[create_actionrow(select)])

#apply command
@slash.slash(name="apply", description=("dont use this"), guild_ids=guild_ids,
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
async def apply(ctx,link,prerecs):
    if not validators.url(link):
        await qembed("Interaction Failed", "The link you submitted was invalid.", "fail", ctx)
        return
    
    c.execute("SELECT MAX(ticket) FROM applications")
    ticket = int(c.fetchall()[0][0]) + 1
    try:
        c.execute("INSERT INTO applications VALUES (?,?,?,?,?,?,NULL)", [ticket, ctx.author.id, link, int(prerecs), "p", datetime.datetime.now()])
        con.commit()
    except:
        await qembed("Interaction Failed", "Sorry, it appears there has been a problem with accessing the application database. Please ping Dworv to ask for help.", "fail", ctx)
        return
    if prerecs == "1": prerecs = True
    else: prerecs = False
    
    await client.reviewing_channel.send(f"{link}",embed=sembed("New Application!", f"Ticket: {ticket}\nLink: {link}\nUser: {ctx.author.name}\nPre-recs = {prerecs}", "ticket"))
    await qembed("Application Successful", f"Thanks for applying! Your ticket is Ticket#{ticket}.", "success", ctx)

#review command
@slash.slash(name="Review",
             description="DEAL THEM PAIN", guild_ids=guild_ids,
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
                    create_choice(name="Reapp", value='d'),
                    create_choice(name="Level 1", value='1'),
                    create_choice(name="Level 2", value='2'),
                    create_choice(name="Level 3", value='3')
                ]
               ),
               create_option(
                 name="overview",
                 description="Give an overview of your opinion of their edit. Be nice and start off with a compliment!",
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

    c.execute("SELECT * FROM applications WHERE ticket = (?)", [ticket])
    row = c.fetchall()
    if row == []:
        await qembed("Interaction Failed", "It appears that there are no applications with that ticket.", "fail", ctx)
        return
    row = row[0]
    if row[4] != "p":
        await qembed("Interaction Failed", "It appears that ticket has already been reviewed.", "fail", ctx)
        return
    member = client.server.get_member(row[1])
    
    link = row[2]
    now = datetime.datetime.now()
    c.execute("UPDATE applications SET revdate = (?) WHERE ticket = (?)", [now, ticket])
    c.execute("UPDATE applications SET status = (?) WHERE ticket = (?)", [status, ticket])
    con.commit()

    if status != "d":
        await member.add_roles(client.member_role)
        if int(status) >= 1: await member.add_roles(client.level_1_role)
        if int(status) >= 2: await member.add_roles(client.level_2_role)
        if int(status) >= 3: await member.add_roles(client.level_3_role)
    
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
    art_embed.set_author(name=f"Application by {member.name}", icon_url=member.avatar_url)

    overview_embed = discord.Embed(title="Overview", description=overview, color=colour)
    overview_embed.set_author(name=f"Review by {ctx.author.name}", icon_url=ctx.author.avatar_url)

    procons_embed = discord.Embed(title="Pros & Cons:", color=colour)
    procons_embed.add_field(name="***[ + ]***", value=pros.replace(", ","\n"), inline=True)
    procons_embed.add_field(name="***[+ / -]***", value=procons.replace(", ","\n"), inline=True)
    procons_embed.add_field(name="***[ - ]***", value=cons.replace(", ","\n"), inline=True)
    
    await client.reviewing_channel.send(embed=art_embed)
    await client.reviewing_channel.send(embed=overview_embed)
    await client.reviewing_channel.send(embed=procons_embed)
    await qembed(f"Ticket #{ticket} reviewed!", "Thanks for reviewing!", "success", ctx)

    if status != "d":
        c.execute("SELECT * FROM roster WHERE user_id = (?)", [member.id])
        if c.fetchall() == []:
            c.execute("INSERT INTO roster VALUES (?,?,NULL,NULL,NULL)", [member.id, status])
            con.commit()
        else:
            c.execute("UPDATE roster SET rank = (?) WHERE user_id = (?)", [status, member.id])
            con.commit()

#roles command
@slash.slash(name="roles", description="Get all your roles here!", guild_ids=guild_ids)
async def roles(ctx):
    content = generate_role_content()
    await ctx.send(embed=content[0], components=content[1])

#profile name command
@slash.subcommand(base="profile", name="name", description="An optional custom name for the roster.", 
                    guild_ids=guild_ids, options=[create_option("name", "Enter your new name!", 3, True)])
async def profile_name(ctx,name):
    if client.member_role not in ctx.author.roles:
        await qembed("Interaction Failed", "You need to be a server member to use this command!", "fail", ctx)
        return
    if len(name) > 16:
        await qembed("Interaction Failed", "The maximum amount of characters is 16!", "fail", ctx)
        return
    c.execute("UPDATE roster SET custom_name = (?) WHERE user_id = (?)", [name, ctx.author.id])
    con.commit()
    await qembed("Name Updated!", f"You have changed your name to: `{name}`", "success", ctx)
    await regenerate_roster_embeds()
    
@slash.subcommand(base="profile", name="bday", description="Set your birthday!", 
                    guild_ids=guild_ids, 
                    options=[
                        create_option("day", "Enter the day of your birthday.", 4, True),
                        create_option("month", "Enter the month of your birthday.", 3, True, choices=[
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
                    ])
                ])
async def profile_birthday(ctx, month, day):
    if client.member_role not in ctx.author.roles:
        await qembed("Interaction Failed", "You need to be a server member to use this command!", "fail", ctx)
        return
    month = int(month)
    days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if 0 < day <= days[month]:
        valid = True
    else:
        valid = False
    if valid == False:
        await qembed("Interaction Failed", "Sorry, it looks like you entered that date wrong. Please make sure you have the day correctly inserted.", "fail", ctx)
        return
    c.execute("UPDATE roster SET birthday = (?) WHERE user_id = (?)", [f"{month},{day}", ctx.author.id])
    con.commit()
    await qembed("Birthday Updated!", "Thanks for updating your birthday!", "success", ctx)

@slash.subcommand(base="profile", name="link", description="Updates your youtube link.", guild_ids=guild_ids,
                     options=[
               create_option(
                 name="link",
                 description="Link for your channel.",    
                 option_type=3,
                 required=True)])
async def profile_link(ctx, link):
    if client.member_role not in ctx.author.roles:
        await qembed("Interaction Failed", "You need to be a server member to use this command!", "fail", ctx)
        return
    valid=validators.url(link)
    if valid != True:
        await qembed("Interaction Failed", "Sorry, it looks like your link is invalid. Please try with a real link (;", "fail", ctx)
        return
    await qembed("Link Updated", "Thanks for updating your link!", "success", ctx)
    c.execute("UPDATE roster SET youtube = (?) WHERE user_id = (?)", [link, ctx.author.id])
    con.commit()
    await regenerate_roster_embeds()

######################################################################################################

#secret
secret = botconfig.load_secret("C:/Users/Ryan/editing/Downfall_Editing_Bots/botconfig.toml", "new")
client.run(secret)
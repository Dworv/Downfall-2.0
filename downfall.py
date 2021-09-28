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

#start msg + client.vars
@client.event
async def on_ready():
    print('Bot Online!')
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name="YouTube", url="https://www.youtube.com/watch?v=QtBDL8EiNZo", details="Apply today!"))
    client.server = client.get_guild(848362097968283668)

    client.user_count_channel = client.server.get_channel(871150395932672020)
    client.member_count_channel = client.server.get_channel(871150597229936672)
    client.join_channel = client.server.get_channel(848567465281978399)

    client.owner_role = client.server.get_role(848379997119184916)
    client.user_role = client.server.get_role(849330016458113035)
    client.member_role = client.server.get_role(858942951980138496)

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
    if commandCount % 4 != 0: 
        pageCount += 1
    optionList = []
    for page in range(1, pageCount+1):
        optionList.append(create_select_option(f"Page {page}", str(page), emoji="1️⃣"))
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
    if ctx.custom_id == "12346":
        await ctx.edit_origin(embed=generate_resource_embed(int(ctx.selected_options[0])))

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

#add-resourse command
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

######################################################################################################

#secret
secret = botconfig.load_secret("C:/Users/Ryan/editing/Downfall_Editing_Bots/botconfig.toml", "new")
client.run(secret)
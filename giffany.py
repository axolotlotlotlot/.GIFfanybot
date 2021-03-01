#.GIFfany-stable
#Author: @slowmachine#9665
################################
import discord
import logging
import sqlite3
import os
import json
from discord.ext import commands
from pretty_help import PrettyHelp
###################################
intents = discord.Intents.default()
intents.members = True
messages = joined = 0
###################################


def get_prefix(client, message):
    db = dataset.connect('sqlite:///journal3.db')
    db.begin()
    prefixes = db.query('SELECT prefix FROM prefixes WHERE guildid = {0}'.format(message.guild.id))
    for prefix in prefixes:
        return prefix['prefix']

bot = commands.Bot(command_prefix= get_prefix, help_command=PrettyHelp(), intents=intents)


@bot.event
async def on_ready():
    print(".GIFfany successfully connected to Discord.")
    print("author:slowmachine#9665")
    await bot.change_presence(activity=discord.Game(name="use .help for commands"))
    bot.unload_extension(f'cogs.logging')


@bot.event
async def on_guild_join(guild):
    db = dataset.connect('sqlite:///journal3.db')
    db.begin()
    table = db['prefixes']
    table.insert(dict(guildid=guild.id, prefix='.'))
    db.commit()

@bot.event
async def on_guild_remove(guild):
    db = dataset.connect('sqlite:///journal3.db')
    db.begin()
    table = db['prefixes']
    table.delete(guildid=guild.id)
    db.commit()

@bot.command(alias='prefix', description='Changes the prefix of the bot for the guild.')
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, prefix):
    """Changes the prefix of the bot for the guild."""
    db = sqlite3.connect('journal3.db')
    cursor = db.cursor()
    sql = ('UPDATE prefixes SET prefix = ? WHERE guildid = ?')
    val = (prefix, ctx.guild.id)
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()
    await ctx.send(f'Prefix has been changed to {prefix}')
    
##########################################################################

@bot.event
async def on_member_ban(guild, member: discord.Member):
    db = dataset.connect('sqlite:///journal3.db')
    db.begin()
    table = db['banned']
    table.insert(dict(guildid=guild.id, userid=member.id))
    db.commit()
    await asyncio.sleep(5)
    main = sqlite3.connect('journal3.db')
    cursor = main.cursor()
    sql = ("DELETE FROM banned WHERE guildid = {0} AND userid = {1}".format(guild.id, member.id))
    cursor.execute(sql)
    main.commit()
    cursor.close()
    main.close()

@bot.event
async def on_member_kick(guild, member: discord.Member):
    db = dataset.connect('sqlite:///journal3.db')
    db.begin()
    table = db['banned']
    table.insert(dict(guildid=guild.id, userid=member.id))
    db.commit()
    await asyncio.sleep(5)
    main = sqlite3.connect('journal3.db')
    cursor = main.cursor()
    sql = ("DELETE FROM banned WHERE guildid = {0} AND userid = {1}".format(guild.id, member.id))
    cursor.execute(sql)
    main.commit()
    cursor.close()
    main.close()

##########################################################################

@bot.command(name='botinfo', aliases=['bot', 'info'])
async def botinfo(ctx):
    '''Shows info about bot'''
    em = discord.Embed(color=discord.Color.green())
    em.title = 'Bot Info'
    em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    try:
        em.description = bot.psa + '\n[Made for r/GravityFalls](https://discord.gg/gravityfalls)'
    except AttributeError:
        em.description = 'A multipurpose bot poorly made by slowmachine#9665\n[Made for r/GravityFalls](https://discord.gg/gravityfalls)'
    em.add_field(name="Servers", value=len(bot.guilds))
    em.add_field(name="Online Users", value=str(len({m.id for m in bot.get_all_members() if m.status is not discord.Status.offline})))
    em.add_field(name='Total Users', value=len(bot.users))
    em.add_field(name='Channels', value=f"{sum(1 for g in bot.guilds for _ in g.channels)}")
    em.add_field(name="Library", value=f"discord.py")
    em.add_field(name="Bot Latency", value=f"{bot.ws.latency * 1000:.0f} ms")
    em.add_field(name='GitHub', value='[Click here](https://github.com/siren15/.GIFfanybot)')
    em.set_footer(text=".GIFfany-bot | Powered by discord.py")
    await ctx.send(embed=em)

##########################################################################

@bot.command()
@commands.has_permissions(administrator=True)
async def disable(ctx, name):
    """Disables commands."""
    await bot.remove_command(name)
    embed = discord.Embed(description=":white_check_mark: Disabled {0}".format(name),
                          timestamp=datetime.utcnow(),
                          color=0x77B255)
    await ctx.send(embed=embed)
@bot.command()
@commands.has_permissions(administrator=True)
async def enable(ctx, name):
    """Enables commands"""
    await bot.remove_command(name)
    embed = discord.Embed(description=":white_check_mark: Enabled {0}".format(name),
                          timestamp=datetime.utcnow(),
                          color=0x77B255)
    await ctx.send(embed=embed)
    
##########################################################################

@bot.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    print(f'unloaded {extension}')
    bot.load_extension(f'cogs.{extension}')
    print(f"loaded {extension}")
    print(f"{extension} reloaded")
    embed = discord.Embed(description=":white_check_mark: Reloaded {0}".format(extension),
                          timestamp=datetime.utcnow(),
                          color=0x77B255)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    """Loads modules. Use: <p>load <module>"""
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"loaded {extension}")
    print(f"loaded {extension}")


@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    """Unloads modules. Use: <p>unload <module>"""
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f"unloaded {extension}")
    print(f"unloaded {extension}")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run('')

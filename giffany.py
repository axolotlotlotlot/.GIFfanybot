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
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


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

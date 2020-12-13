#Zephyrus-rewrite
#Author: @slowmachine#9665
################################
import discord
import asyncio
import os
import json
from secrets import randbelow
from discord.ext import commands
from pretty_help import PrettyHelp
###################################
intents = discord.Intents.default()
intents.members = True
messages = joined = 0
###################################

def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]

bot = commands.Bot(command_prefix= get_prefix, help_command=PrettyHelp(), intents=intents)


@bot.event
async def on_ready():
    print("Zephyrus successfully connected to Discord.")
    print("author:slowmachine#9665")
    await bot.change_presence(activity=discord.Game(name="use .help for commands"))



@bot.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = 'z!'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@bot.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@bot.command(alias='prefix')
@commands.has_permissions(administrator=True)
async  def changeprefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)
    await ctx.send(f'Prefix has been changed to {get_prefix}')

##########################################################################
@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.channel.send(f"{extension} loaded.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.channel.send(f"{extension} unloaded.")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run('token')

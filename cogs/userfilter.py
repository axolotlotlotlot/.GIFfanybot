import discord
import sqlite3
import datetime
import dataset
import asyncio
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Greedy, CheckFailure


class UserFilter(commands.Cog):
    """Tags module"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['uf'], invoke_without_command=True)
    @commands.has_permissions(ban_members=True)
    async def userfilter(self, ctx):
        embed = Embed(description="This command adds users to a filter so that they cannot use commands that have a filter on them. \nTo add someone to a filter use: `.userfilter add 'member'` \nTo remove use: `.userfilter remove 'member'`\nAliases: `uf`",
                      colour=0x237CCD
        )
        await ctx.send(embed=embed)

    @userfilter.command()
    @commands.has_permissions(ban_members=True)
    async def add(self, ctx, member: discord.Member=None, *, reason=None):
      modrole = discord.utils.get(ctx.guild.roles, name="Mods")
      if modrole in ctx.author.roles:
          if member == ctx.author:
              embed = Embed(
                  description=":x: You cannot filter yourself!",
                  color=0xDD2222)
              await ctx.send(embed=embed)
              return

          if member == None:
              embed = Embed(
                  description=":x: Please provide a user!",
                  color=0xDD2222)
              await ctx.send(embed=embed)
              return

          if reason == None:
              reason = "No reason provided."

          db = dataset.connect('sqlite:///journal3.db')
          db.begin()
          table = db['userfilter']
          users = table.find(guild=ctx.guild.id, user=member.id)
          for user in users:
              if user['user'] == member.id:
                  embed = Embed(
                      description=":x: That member is already in the filter!",
                      color=0xDD2222)
                  await ctx.send(embed=embed)
                  return
              else:
                  table.insert(dict(guild=ctx.guild.id, user=member.id))
                  db.commit()
                  embed = discord.Embed(
                      description=f":white_check_mark: {member.mention} was added to the filter \nFor: {reason}",
                      timestamp=datetime.utcnow(),
                      color=0x77B255)
                  embed.set_footer(text=f'Auctioned by: {ctx.author} / {ctx.author.id}')
                  await ctx.send(embed=embed)

    @add.error
    async def uf_add_error(self, ctx, exc):
      if isinstance(exc, CheckFailure):
          embed = Embed(
              description=f":x: You have insufficient permissions to perform this action",
              color=0xDD2222)
          await ctx.send(embed=embed)

    @userfilter.command(aliases=['filterremove', 'whitelist', 'fdelete', 'filterdelete'])
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx, member: discord.Member = None, *, reason=None):
      db = dataset.connect('sqlite:///journal3.db')
      db.begin()
      table = db['userfilter']
      users = table.all(guild=ctx.guild.id, user=ctx.author.id)
      for user in users:
          if user['user'] == ctx.author.id:
              embed = Embed(
                  description=":x: You can't unfilter yourself!",
                  color=0xDD2222)
              await ctx.send(embed=embed)
              return

      if member == ctx.author:
          embed = Embed(
              description=":x: You can't unfilter yourself!",
              color=0xDD2222)
          await ctx.send(embed=embed)
          return

      if member == None:
          embed = Embed(
              description=":x: Please provide a user!",
              color=0xDD2222)
          await ctx.send(embed=embed)
          return

      if reason == None:
          reason = "No reason provided."

      db = dataset.connect('sqlite:///journal3.db')
      db.begin()
      table = db['userfilter']
      users = table.find(guild=ctx.guild.id, user=member.id)
      for user in users:
          if user['user'] != member.id:
              embed = Embed(
                  description=":x: Can't find that member in the filter!",
                  color=0xDD2222)
              await ctx.send(embed=embed)
              return
          else:
              table.delete(guild=ctx.guild.id, user=member.id)
              db.commit()
              embed = discord.Embed(description=f":white_check_mark: {member.mention} was removed from the list of spammy users \nFor: {reason}",
                                    timestamp=datetime.utcnow(),
                                    color=0x77B255)
              embed.set_footer(text=f'Auctioned by: {ctx.author} / {ctx.author.id}')
              await ctx.send(embed=embed)

    @remove.error
    async def uf_remove_error(self, ctx, exc):
      if isinstance(exc, CheckFailure):
          embed = Embed(
              description=f":x: You have insufficient permissions to perform this action",
              color=0xDD2222)
          await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(UserFilter(bot))
    print('user filter module loaded')

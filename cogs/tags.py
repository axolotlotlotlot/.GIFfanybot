import discord
import sqlite3
import datetime
import dataset
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Greedy, CheckFailure


class Tags(commands.Cog):
    """Tags module"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['t'], invoke_without_command=True)
    @commands.has_role('Mystery Twins')
    async def tag(self, ctx, tag_Name=None):
        """To create a tag use <p>tag create <name of the tag> <content> To recall a tag use <p>tag <name of the tag>"""
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['userfilter']
        users = table.all(guild=ctx.guild.id, user=ctx.author.id)
        for user in users:
            if user['user'] == ctx.author.id:
                embed = Embed(
                    description=":x: You're not allowed to use this command!",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                return

        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)
        tagcontent = field("SELECT content FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)

        if tag_Name == None:
            embed = Embed(
                description=":x: Please provide a tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if tag_Name != tagname:
            embed = Embed(
                description=":x: Couldn't find that tag",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if tag_Name == tagname:
            await ctx.send(f"{tagcontent}")
            return

        db.commit()
        cursor.close()
        db.close()


    @tag.error
    async def tag_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            embed = Embed(description=f":x: You currently are not high enough role to use this command. Please level up to Mystery Twins to use it.",
                          color=0xDD2222)
            await ctx.send(embed=embed)

    @tag.command(aliases=['filteradd', 'blacklist'])
    @commands.has_permissions(ban_members=True)
    async def fadd(self, ctx, member: discord.Member=None, *, reason=None):
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
            table.insert(dict(guild=ctx.guild.id, user=member.id))
            db.commit()
            embed = discord.Embed(
                description=f":white_check_mark: {member.mention} was added to the list of spammy users \nFor: {reason}",
                timestamp=datetime.utcnow(),
                color=0x77B255)
            embed.set_footer(text=f'Auctioned by: {ctx.author} / {ctx.author.id}')
            await ctx.send(embed=embed)

    @fadd.error
    async def tag_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            embed = Embed(
                description=f":x: You have insufficient permissions to perform this action",
                color=0xDD2222)
            await ctx.send(embed=embed)

    @tag.command(aliases=['filterremove', 'whitelist', 'fdelete', 'filterdelete'])
    @commands.has_permissions(ban_members=True)
    async def fremove(self, ctx, member: discord.Member = None, *, reason=None):
        if member == ctx.author:
            embed = Embed(
                description=":x: You cannot unfilter yourself!",
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
        table.delete(guild=ctx.guild.id, user=member.id)
        db.commit()
        embed = discord.Embed(description=f":white_check_mark: {member.mention} was removed from the list of spammy users \nFor: {reason}",
                              timestamp=datetime.utcnow(),
                              color=0x77B255)
        embed.set_footer(text=f'Auctioned by: {ctx.author} / {ctx.author.id}')
        await ctx.send(embed=embed)

    @fremove.error
    async def tag_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            embed = Embed(
                description=f":x: You have insufficient permissions to perform this action",
                color=0xDD2222)
            await ctx.send(embed=embed)

    @tag.command()
    async def create(self, ctx, tag_Name=None, *, content=None):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)

        if tag_Name == None:
            embed = Embed(
                description=":x: Please provide a tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if content == None:
            embed = Embed(
                description=":x: Please provide tag content",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if tag_Name == tagname:
            embed = Embed(
                description=":x: Tag with that name already exists",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if tag_Name != tagname:
            db = dataset.connect('sqlite:///journal3.db')
            db.begin()
            table = db['tag']
            table.insert(dict(guild_id=ctx.guild.id, author_id=ctx.author.id, names=tag_Name, content=content))
            db.commit()
            embed = discord.Embed(title="Tag created",
                                  timestamp=datetime.datetime.utcnow(),
                                  color=discord.Colour.from_rgb(76, 150, 255))
            embed.add_field(name=f"{tag_Name}", value=f"{content}", inline=False)
            embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
            await ctx.send(embed=embed)

        db.commit()
        cursor.close()
        db.close()

    @tag.command()
    async def edit(self, ctx, tag_Name=None, *, content=None):
        db = sqlite3.connect('journal3.db', check_same_thread=False)
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)
        author = field("SELECT author_id FROM tag WHERE guild_id = ? AND names = ? AND author_id = ?",
                       ctx.guild.id, tag_Name, ctx.author.id)

        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        tagnames = db.query('SELECT names FROM tag WHERE guild_id = {0} AND names = {1}'.format(ctx.guild.id, tag_Name))
        authors = db.query('SELECT author_id FROM tag WHERE guild_id = {0} AND names = {1} AND author_id = {2}'
                           .format(ctx.guild.id, tag_Name, ctx.author.id))

        if tag_Name == None:
            embed = Embed(
                description=":x: Please provide a tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)

        elif content == None:
            embed = Embed(
                description=":x: Please provide tag content",
                color=0xDD2222)
            await ctx.send(embed=embed)


        elif tag_Name != tagname:
            embed = Embed(
                description=":x: Couldn't find that tag",
                color=0xDD2222)
            await ctx.send(embed=embed)

        for author in authors:
            if ctx.author.id == author['author_id']:
                for tagname in tagnames:
                    if tag_Name == tagname['names']:
                        sql = ('UPDATE tag SET content = ? WHERE guild_id = ? AND author_id = ? AND names = ?')
                        val = (content, ctx.guild.id, ctx.author.id, tag_Name)
                        cursor.execute(sql, val)
                        embed = discord.Embed(title="Tag updated",
                                              timestamp=datetime.datetime.utcnow(),
                                              color=discord.Colour.from_rgb(76, 150, 255))
                        embed.add_field(name=f"{tag_Name}", value=f"{content}", inline=False)
                        embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("Couldn't find that tag")
            else:
                await ctx.send("You're not the author of this tag. Only authors can edit their tags.")
        #if author == ctx.author.id:
            #if tag_Name == tagname:

            #else:
                #await ctx.send("Couldn't find that tag")
        #else:
            #await ctx.send("You're not the author of this tag. Only authors can edit their tags.")

        db.commit()
        cursor.close()
        db.close()

    @tag.command()
    async def delete(self, ctx, tagName=None):
        if tagName == None:
            embed = Embed(
                description=":x: Please provide tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['tag']
        tags = table.all(names=f'{tagName}', guild_id=ctx.guild.id, author_id=ctx.author.id)
        for tag in tags:
            if tag['names'] == tagName:
                table.delete(names=f'{tagName}', guild_id=ctx.guild.id, author_id=ctx.author.id)
                db.commit()
                embed = discord.Embed(title="Tag deleted",
                                      description=f"{tagName} was deleted by {ctx.author.mention}",
                                      timestamp=datetime.datetime.utcnow(),
                                      color=discord.Colour.from_rgb(76, 150, 255))
                embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
                await ctx.send(embed=embed)

    @tag.command()
    @commands.has_permissions(administrator=True)
    async def adelete(self, ctx, tagName=None):
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        if tagName == None:
            await ctx.send("Please provide a tag name")
            return
        table = db['tag']
        tags = table.all(names=f'{tagName}', guild_id=ctx.guild.id)
        for tag in tags:
            if tag['names'] == tagName:
                table.delete(names=f'{tagName}', guild_id=ctx.guild.id)
                db.commit()
                embed = discord.Embed(title="Tag deleted by an administrator",
                                      description=f"{tagName} was deleted by {ctx.author.mention}",
                                      timestamp=datetime.datetime.utcnow(),
                                      color=discord.Colour.from_rgb(76, 150, 255))
                embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
                await ctx.send(embed=embed)
                return
            if tag['names'] != tagName:
                await ctx.send(f"{tagName} was not found")
                return

    @adelete.error
    async def tag_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            embed = Embed(
                description=f":x: You have insufficient permissions to perform this action",
                color=0xDD2222)
            await ctx.send(embed=embed)

    @tag.command()
    @commands.has_permissions(administrator=True)
    async def aedit(self, ctx, tag_Name=None, *, content=None):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tags WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)

        if tag_Name == None:
            embed = Embed(
                description=":x: Please provide a tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)

        elif content == None:
            embed = Embed(
                description=":x: Please provide tag content",
                color=0xDD2222)
            await ctx.send(embed=embed)


        elif tag_Name != tagname:
            embed = Embed(
                description=":x: Couldn't find that tag",
                color=0xDD2222)
            await ctx.send(embed=embed)

        elif tag_Name == tagname:
            sql = ("UPDATE tags SET content = ? WHERE guild_id = ? AND names = ?")
            val = (content, ctx.guild.id, tag_Name)
            cursor.execute(sql, val)
            embed = discord.Embed(title="Tag updated by an administrator",
                                  timestamp=datetime.datetime.utcnow(),
                                  color=discord.Colour.from_rgb(76, 150, 255))
            embed.add_field(name=f"{tag_Name}", value=f"{content}", inline=False)
            embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
            await ctx.send(embed=embed)

        db.commit()
        cursor.close()
        db.close()

    @aedit.error
    async def tag_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            embed = Embed(
                description=f":x: You have insufficient permissions to perform this action",
                color=0xDD2222)
            await ctx.send(embed=embed)

    @tag.command()
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        """Fake ban member from guild. Use: <p>tag ban <member(s)> <reason>"""
        if member == ctx.message.author:
            embed = Embed(
                description=":x: You cannot ban yourself!",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if member == None:
            embed = Embed(
                description=":x: Please provide a a user!",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if reason == None:
            reason = "No reason provided."
        embed = discord.Embed(description=f":white_check_mark: {member.mention} was yeeted from {ctx.guild} for {reason} by {ctx.author.mention}",
                              timestamp=datetime.utcnow(),
                              color=0x77B255)
        await ctx.send(embed=embed, reason=reason)

    @tag.command()
    async def list(self, ctx):
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        msg = 'List of all tags:\n'

        for i in db['tag']:
            msg = msg + '**' + i['names'] + '**\n'

        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Tags(bot))
    print('tags module loaded')

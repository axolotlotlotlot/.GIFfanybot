import discord
import sqlite3
import datetime
import dataset
from discord.ext import commands


class Tags(commands.Cog):
    """Tags module"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, tag_Name=None):
        """Lets me store and recall messages and image links. To create a tag use <p>tag create <name of the tag> <content> To recall a tag use <p>tag <name of the tag>"""
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)
        tagcontent = field("SELECT content FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)

        if tag_Name == None:
            await ctx.send("Please provide a tag name")
            return

        if tag_Name != tagname:
            await ctx.send("Couldn't find that tag")
            return

        if tag_Name == tagname:
            await ctx.send(f"{tagcontent}")
            return

        db.commit()
        cursor.close()
        db.close()

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
            await ctx.send("Please provide a tag name")
            return

        if content == None:
            await ctx.send("Please provide tag content")
            return

        if tag_Name == tagname:
            await ctx.send("Tag with that name already exists")
            return

        if tag_Name != tagname:
            sql = ("INSERT INTO tag(guild_id, author_id, names, content) VALUES(?, ?, ?, ?)")
            val = (ctx.guild.id, ctx.author.id, tag_Name, content)
            embed = discord.Embed(title="Tag created",
                                  timestamp=datetime.datetime.utcnow(),
                                  color=discord.Colour.from_rgb(76, 150, 255))
            embed.add_field(name=f"{tag_Name}", value=f"{content}", inline=False)
            embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
            await ctx.send(embed=embed)

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @tag.command()
    async def edit(self, ctx, tag_Name=None, *, content=None):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)
        author = field("SELECT author_id FROM tag WHERE guild_id = ? AND names = ? AND author_id = ?",
                       ctx.guild.id, tag_Name, ctx.author.id)

        if tag_Name == None:
            await ctx.send("Please provide a tag name")
            return

        if content == None:
            await ctx.send("Please provide tag content")
            return

        if tag_Name != tagname:
            await ctx.send("Couldn't find that tag")
            return

        if author != ctx.author.id:
            await ctx.send("You're not the author of this tag. Only authors can edit their tags.")

        elif author == ctx.author.id:

            if tag_Name == tagname:
                sql = ("UPDATE tag SET content = ? WHERE guild_id = ? AND names = ? AND author_id = ?")
                val = (content, ctx.guild.id, tag_Name, ctx.author.id)
                embed = discord.Embed(title="Tag updated",
                                      timestamp=datetime.datetime.utcnow(),
                                      color=discord.Colour.from_rgb(76, 150, 255))
                embed.add_field(name=f"{tag_Name}", value=f"{content}", inline=False)
                embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
                await ctx.send(embed=embed)

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @tag.command()
    async def delete(self, ctx, tagName=None):
        if tagName == None:
            await ctx.send("Please provide a tag name")
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
    async def mdelete(self, ctx, tagName=None):
        modrole = discord.utils.get(ctx.guild.roles, name="Mods")
        if modrole not in ctx.author.roles:
            await ctx.send("You have insufficient permissions to do this action")
            return
        if modrole in ctx.author.roles:
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
                    embed = discord.Embed(title="Tag deleted by a moderator",
                                          description=f"{tagName} was deleted by {ctx.author.mention}",
                                          timestamp=datetime.datetime.utcnow(),
                                          color=discord.Colour.from_rgb(76, 150, 255))
                    embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
                    await ctx.send(embed=embed)
                    return
                if tag['names'] != tagName:
                    await ctx.send(f"{tagName} was not found")
                    return

    @tag.command()
    async def medit(self, ctx, tag_Name=None, *, content=None):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tags WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)
        modrole = discord.utils.get(ctx.guild.roles, name="Mods")

        if modrole not in ctx.author.roles:
            await ctx.send("You have insufficient permissions to do this action")

        elif tag_Name == None:
            await ctx.send("Please provide a tag name")


        elif content == None:
            await ctx.send("Please provide tag content")


        elif tag_Name != tagname:
            await ctx.send("Couldn't find that tag")


        elif tag_Name == tagname:
            sql = ("UPDATE tags SET content = ? WHERE guild_id = ? AND names = ?")
            val = (content, ctx.guild.id, tag_Name)
            embed = discord.Embed(title="Tag updated by a moderator",
                                  timestamp=datetime.datetime.utcnow(),
                                  color=discord.Colour.from_rgb(76, 150, 255))
            embed.add_field(name=f"{tag_Name}", value=f"{content}", inline=False)
            embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
            await ctx.send(embed=embed)

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @tag.command()
    async def list(self, ctx):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        cursor.execute("SELECT names FROM tags WHERE guild_id = {0}".format(ctx.guild.id))
        rows = cursor.fetchall()
        await ctx.send(rows)

        db.commit()
        cursor.close()
        db.close()

    @commands.group(invoke_without_command=True)
    async def t(self, ctx, tag_Name=None):
        """a shorter way of dealing with tags"""
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)
        tagcontent = field("SELECT content FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)

        if tag_Name == None:
            await ctx.send("Please provide a tag name")
            return

        if tag_Name != tagname:
            await ctx.send("Couldn't find that tag")
            return

        if tag_Name == tagname:
            await ctx.send(f"{tagcontent}")
            return

        db.commit()
        cursor.close()
        db.close()

    @t.command()
    async def create(self, ctx, tag_Name=None, *, content=None):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)

        if tag_Name == None:
            await ctx.send("Please provide a tag name")
            return

        if content == None:
            await ctx.send("Please provide tag content")
            return

        if tag_Name == tagname:
            await ctx.send("Tag with that name already exists")
            return

        if tag_Name != tagname:
            sql = ("INSERT INTO tag(guild_id, author_id, names, content) VALUES(?, ?, ?, ?)")
            val = (ctx.guild.id, ctx.author.id, tag_Name, content)
            embed = discord.Embed(title="Tag created",
                                  timestamp=datetime.datetime.utcnow(),
                                  color=discord.Colour.from_rgb(76, 150, 255))
            embed.add_field(name=f"{tag_Name}", value=f"{content}", inline=False)
            embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
            await ctx.send(embed=embed)

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @t.command()
    async def edit(self, ctx, tag_Name=None, *, content=None):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)
        author = field("SELECT author_id FROM tag WHERE guild_id = ? AND names = ? AND author_id = ?",
                       ctx.guild.id, tag_Name, ctx.author.id)

        if tag_Name == None:
            await ctx.send("Please provide a tag name")
            return

        if content == None:
            await ctx.send("Please provide tag content")
            return

        if tag_Name != tagname:
            await ctx.send("Couldn't find that tag")
            return

        if author != ctx.author.id:
            await ctx.send("You're not the author of this tag. Only authors can edit their tags.")

        elif author == ctx.author.id:

            if tag_Name == tagname:
                sql = ("UPDATE tag SET content = ? WHERE guild_id = ? AND names = ? AND author_id = ?")
                val = (content, ctx.guild.id, tag_Name, ctx.author.id)
                embed = discord.Embed(title="Tag updated",
                                      timestamp=datetime.datetime.utcnow(),
                                      color=discord.Colour.from_rgb(76, 150, 255))
                embed.add_field(name=f"{tag_Name}", value=f"{content}", inline=False)
                embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
                await ctx.send(embed=embed)

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @t.command()
    async def delete(self, ctx, tagName=None):
        if tagName == None:
            await ctx.send("Please provide a tag name")
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

    @t.command()
    async def mdelete(self, ctx, tagName=None):
        modrole = discord.utils.get(ctx.guild.roles, name="Mods")
        if modrole not in ctx.author.roles:
            await ctx.send("You have insufficient permissions to do this action")
            return
        if modrole in ctx.author.roles:
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
                    embed = discord.Embed(title="Tag deleted by a moderator",
                                          description=f"{tagName} was deleted by {ctx.author.mention}",
                                          timestamp=datetime.datetime.utcnow(),
                                          color=discord.Colour.from_rgb(76, 150, 255))
                    embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
                    await ctx.send(embed=embed)
                    return
                if tag['names'] != tagName:
                    await ctx.send(f"{tagName} was not found")
                    return

    @t.command()
    async def medit(self, ctx, tag_Name=None, *, content=None):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tags WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)
        modrole = discord.utils.get(ctx.guild.roles, name="Mods")

        if modrole not in ctx.author.roles:
            await ctx.send("You have insufficient permissions to do this action")

        elif tag_Name == None:
            await ctx.send("Please provide a tag name")


        elif content == None:
            await ctx.send("Please provide tag content")


        elif tag_Name != tagname:
            await ctx.send("Couldn't find that tag")


        elif tag_Name == tagname:
            sql = ("UPDATE tags SET content = ? WHERE guild_id = ? AND names = ?")
            val = (content, ctx.guild.id, tag_Name)
            embed = discord.Embed(title="Tag updated by a moderator",
                                  timestamp=datetime.datetime.utcnow(),
                                  color=discord.Colour.from_rgb(76, 150, 255))
            embed.add_field(name=f"{tag_Name}", value=f"{content}", inline=False)
            embed.set_footer(text="Author ID:{0}".format(ctx.author.id))
            await ctx.send(embed=embed)

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @t.command()
    async def list(self, ctx):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        cursor.execute("SELECT names FROM tags WHERE guild_id = {0}".format(ctx.guild.id))
        rows = cursor.fetchall()
        await ctx.send(rows)

        db.commit()
        cursor.close()
        db.close()


def setup(bot):
    bot.add_cog(Tags(bot))
    print('tags module loaded')

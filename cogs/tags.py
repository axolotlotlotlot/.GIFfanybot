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
        """[Mystery Twins] Lets me store and recall messages and image links. To create a tag use <p>tag create <name of the tag> <content> To recall a tag use <p>tag <name of the tag>"""
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['userfilter']
        users = table.all(guild=ctx.guild.id, user=ctx.author.id)
        for user in users:
            if user['user'] == ctx.author.id:
                await ctx.send("You're not allowed to use this command")
                return

        MT = discord.utils.get(ctx.guild.roles, name="Mystery Twins")
        if MT in ctx.author.roles:
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
        else:
            await ctx.send("You currently are not high enough role to use this command. Please level up to Mystery Twins to use it.")

    @tag.command()
    async def fadd(self, ctx, member: discord.Member=None, *, reason=None):
        modrole = discord.utils.get(ctx.guild.roles, name="Mods")
        if modrole not in ctx.author.roles:
            await ctx.send("You have insufficient permissions to do this action")
            return
        if modrole in ctx.author.roles:
            if member == ctx.author:
                await ctx.channel.send("You cannot filter yourself!")
                return

            if member == None:
                await ctx.channel.send("Please provide a user!")
                return

            if reason == None:
                reason = "No reason provided."

            db = dataset.connect('sqlite:///journal3.db')
            db.begin()
            table = db['userfilter']
            table.insert(dict(guild=ctx.guild.id, user=member.id))
            db.commit()
            await ctx.send(f"{member.mention} was added to the list of spammy users \nFor: {reason} \nBy: {ctx.author.mention} \nMember ID: {member.id}")

    @tag.command()
    async def fremove(self, ctx, member: discord.Member = None, *, reason=None):
        modrole = discord.utils.get(ctx.guild.roles, name="Mods")
        if modrole not in ctx.author.roles:
            await ctx.send("You have insufficient permissions to do this action")
            return
        if modrole in ctx.author.roles:
            if member == ctx.author:
                await ctx.channel.send("You cannot unfilter yourself!")
                return

            if member == None:
                await ctx.channel.send("Please provide a user!")
                return

            if reason == None:
                reason = "No reason provided."

            db = dataset.connect('sqlite:///journal3.db')
            db.begin()
            table = db['userfilter']
            table.delete(guild=ctx.guild.id, user=member.id)
            db.commit()
            await ctx.send(f"{member.mention} was removed from the list of spammy users \nFor: {reason} \nBy: {ctx.author.mention} \nMember ID: {member.id}")

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
            return

        if author == ctx.author.id:
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
    
    @commands.group(invoke_without_command=True)
    async def t(self, ctx, tag_Name=None):
        """A shorter way of dealing with tags"""
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['userfilter']
        users = table.all(guild=ctx.guild.id, user=ctx.author.id)
        for user in users:
            if user['user'] == ctx.author.id:
                await ctx.send("You're not allowed to use this command")
                return

        MT = discord.utils.get(ctx.guild.roles, name="Mystery Twins")
        if MT in ctx.author.roles:
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
        else:
            await ctx.send("You currently are not high enough role to use this command. Please level up to Mystery Twins to use it.")

    @t.command()
    async def fadd(self, ctx, member: discord.Member=None, *, reason=None):
        modrole = discord.utils.get(ctx.guild.roles, name="Mods")
        if modrole not in ctx.author.roles:
            await ctx.send("You have insufficient permissions to do this action")
            return
        if modrole in ctx.author.roles:
            if member == ctx.author:
                await ctx.channel.send("You cannot filter yourself!")
                return

            if member == None:
                await ctx.channel.send("Please provide a user!")
                return

            if reason == None:
                reason = "No reason provided."

            db = dataset.connect('sqlite:///journal3.db')
            db.begin()
            table = db['userfilter']
            table.insert(dict(guild=ctx.guild.id, user=member.id))
            db.commit()
            await ctx.send(f"{member.mention} was added to the list of spammy users \nFor: {reason} \nBy: {ctx.author.mention} \nMember ID: {member.id}")

    @t.command()
    async def fremove(self, ctx, member: discord.Member = None, *, reason=None):
        modrole = discord.utils.get(ctx.guild.roles, name="Mods")
        if modrole not in ctx.author.roles:
            await ctx.send("You have insufficient permissions to do this action")
            return
        if modrole in ctx.author.roles:
            if member == ctx.author:
                await ctx.channel.send("You cannot unfilter yourself!")
                return

            if member == None:
                await ctx.channel.send("Please provide a user!")
                return

            if reason == None:
                reason = "No reason provided."

            db = dataset.connect('sqlite:///journal3.db')
            db.begin()
            table = db['userfilter']
            table.delete(guild=ctx.guild.id, user=member.id)
            db.commit()
            await ctx.send(f"{member.mention} was removed from the list of spammy users \nFor: {reason} \nBy: {ctx.author.mention} \nMember ID: {member.id}")

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
            return

        if author == ctx.author.id:
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
    
    @tag.command()
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        """Fake ban member from guild. Use: <p>tag ban <member(s)> <reason>"""
        if member == ctx.message.author:
            await ctx.channel.send("You cannot ban yourself!")
            return

        if member == None:
            await ctx.channel.send("Please provide a user!")
            return

        if reason == None:
            reason = "No reason provided."
        await ctx.channel.send(f"{member.mention} was yeeted from {ctx.guild} for {reason} by {ctx.author.mention}")
    
    @t.command()
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        """Fake ban member from guild. Use: <p>tag ban <member(s)> <reason>"""
        if member == ctx.message.author:
            await ctx.channel.send("You cannot ban yourself!")
            return

        if member == None:
            await ctx.channel.send("Please provide a user!")
            return

        if reason == None:
            reason = "No reason provided."
        await ctx.channel.send(f"{member.mention} was yeeted from {ctx.guild} for {reason} by {ctx.author.mention}")
    
    @tag.command()
    async def list(self, ctx):
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        msg = 'List of all tags:\n'

        for i in db['tag']:
            msg = msg + '**' + i['names'] + '**\n'

        await ctx.send(msg)
    
    @t.command()
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

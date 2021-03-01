import discord
import sqlite3
import datetime
import dataset
import asyncio
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Greedy, CheckFailure


class Tags(commands.Cog):
    """Tags module"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['t'], invoke_without_command=True)
    @commands.has_role('Mystery Twins')
    async def tag(self, ctx, *,tag_Name=None):
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

        table2 = db['tag']
        tagnames = table2.find(names={'ilike': f'{tag_Name}'}, guild_id=ctx.channel.guild.id)
        nms = ''
        for tn in tagnames:
            nms = nms + f"{tn['names'].lower()}" + ', '
        names = nms.split(',')

        tagscontent = table2.distinct('content', names={'ilike': f'{tag_Name}'}, guild_id=ctx.channel.guild.id)
        for tc in tagscontent:
            tagcontent = tc['content']

        if tag_Name == None:
            embed = Embed(
                description=":x: Please provide a tag name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if tag_Name.lower() not in names:
            embed = Embed(
                description=":x: Couldn't find that tag",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if tag_Name.lower() in names:
            await ctx.send(f"{tagcontent}")
            return

    @tag.error
    async def tag_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            embed = Embed(description=f":x: You currently are not high enough role to use this command. Please level up to Mystery Twins to use it.",
                          color=0xDD2222)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        dbs = sqlite3.connect('journal3.db')
        cursor = dbs.cursor()
        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        prefix = field('SELECT prefix FROM prefixes WHERE guildid = {0}'.format(message.guild.id))
        cursor.close
        dbs.close
        create = f'{prefix}t create'
        cr = f'{prefix}tag create'
        if message.content == create or message.content == cr:
            channel = message.channel
            embed = discord.Embed(
                description="Tag creation started. Please provide a tag name. I will save your next message as the tag name, or type `abort` to abort the process.",
                color=message.author.top_role.colour)
            startembed = await channel.send(embed=embed)

            def check(m):
                return m.channel == channel and m.author == message.author

            while True:
                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=check)

                except asyncio.TimeoutError:
                        embed = Embed(
                            description=f":x: Uh oh, {message.author.mention}! You took longer than 1 minute to respond, tag creation cancelled.",
                            color=0xDD2222)
                        await channel.send(embed=embed)
                        await startembed.delete()
                        await message.delete()
                        break

                abort = ['abort', 'Abort', 'ABort', 'ABOrt', 'ABORt', 'ABORT', 'aBORT', 'abORT', 'aboRT', 'aborT']

                if msg.content in abort:
                    embed = Embed(
                        description=":x: Tag creation process aborted",
                        color=0xDD2222)
                    await channel.send(embed=embed)
                    await startembed.delete()
                    await msg.delete()
                    await message.delete()
                    return

                elif msg.content not in abort:
                    table = db['tag']
                    tagnames = table.find(names={'ilike': f'{msg.content}'}, guild_id=message.channel.guild.id)
                    nms = ''
                    for tn in tagnames:
                        nms = nms + f"{tn['names'].lower()}" + ' '
                    name = nms.split(' ')
                    cntnt = msg.content
                    content = cntnt.lower()
                    if content in name:
                        embed = Embed(
                            description=":x: Tag with that name already exists, try again",
                            color=0xDD2222)
                        await channel.send(embed=embed)
                        await msg.delete()
                    if content not in name:
                        embed = discord.Embed(
                            description=f"Tag's name is `{msg.content}`. Now please provide tag content. I will save your next message as the tag content, or type `abort` to abort the process.",
                            color=message.author.top_role.colour)
                        msgembed = await channel.send(embed=embed)
                        try:
                            contentmsg = await self.bot.wait_for('message', timeout=60.0, check=check)

                        except asyncio.TimeoutError:
                                embed = Embed(
                                    description=f":x: Uh oh, {message.author.mention}! You took longer than 1 minute to respond, tag creation cancelled.",
                                    color=0xDD2222)
                                await channel.send(embed=embed)
                                await startembed.delete()
                                await msg.delete()
                                await msgembed.delete()
                                await message.delete()

                        if contentmsg.content in abort:
                            embed = Embed(
                                description=":x: Tag creation process aborted",
                                color=0xDD2222)
                            await channel.send(embed=embed)
                            await startembed.delete()
                            await msg.delete()
                            await msgembed.delete()
                            await contentmsg.delete()
                            await message.delete()
                            return

                        elif contentmsg.attachments:
                            for url in contentmsg.attachments:
                                table.insert(dict(guild_id=channel.guild.id, author_id=message.author.id, names=msg.content, content=url.url))
                                db.commit()
                                embed = discord.Embed(title=":white_check_mark: Tag created",
                                                      timestamp=datetime.datetime.utcnow(),
                                                      color=0x77B255)
                                embed.add_field(name=f"Tag name: {msg.content}", value=f"Tag content: \n{url.url}", inline=False)
                                embed.set_footer(text="Author ID:{0}".format(message.author.id))
                                await channel.send(embed=embed)
                                await startembed.delete()
                                await msg.delete()
                                await msgembed.delete()
                                #await contentmsg.delete()
                                await message.delete()
                                return
                        else:
                            table.insert(dict(guild_id=channel.guild.id, author_id=message.author.id, names=msg.content, content=contentmsg.content))
                            db.commit()
                            embed = discord.Embed(title=":white_check_mark: Tag created",
                                                  timestamp=datetime.datetime.utcnow(),
                                                  color=0x77B255)
                            embed.add_field(name=f"Tag name: {msg.content}", value=f"Tag content: \n{contentmsg.content}", inline=False)
                            embed.set_footer(text="Author ID:{0}".format(message.author.id))
                            await channel.send(embed=embed)
                            await startembed.delete()
                            await msg.delete()
                            await msgembed.delete()
                            await contentmsg.delete()
                            await message.delete()
                            return



    @tag.command(aliases=['c'])
    async def create(self, ctx, tag_Name=None, *, content=None):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        tagname = field("SELECT names FROM tag WHERE guild_id = ? AND names = ?", ctx.guild.id, tag_Name)

        if tag_Name == None:
#            embed = Embed(
#               description=":x: Please provide a tag name",
#                color=0xDD2222)
#            await ctx.send(embed=embed)
            return

        if content == None:
#            embed = Embed(
#                description=":x: Please provide tag content",
#                color=0xDD2222)
#            await ctx.send(embed=embed)
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

        elif tag_Name == tagname:
            embed = Embed(
                description=":x: Tag with that name already exists",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

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
    async def list(self, ctx):
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['tag']
        guildids = table.distinct('guild_id', guild_id=ctx.guild.id)
        names = table.distinct('names', guild_id=ctx.guild.id)
        msg = 'List of all tags:\n'

        for i in names:
            msg = msg + '**' + i['names'] + '**\n'

        if i['names'] is not None:
            await ctx.send(msg)
        else:
            embed = Embed(
                description=":x: Couldn't find any tags for this server.",
                color=0xDD2222)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Tags(bot))
    print('tags module loaded')

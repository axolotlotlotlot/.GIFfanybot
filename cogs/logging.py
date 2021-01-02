import discord
import sqlite3
import datetime
from discord.ext import commands




class Logging(commands.Cog):
    """Guild logging module"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_role('Mods')
    async def logging(self, ctx):
        """Sets guilds log channel. Use:<p>logging channel <channel>"""
        await ctx.send('Available setup commands: \nlogging channel <channel>')

    @logging.command()
    async def channel(self, ctx, channel: discord.TextChannel):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO logs(guild_id, channel_id) VALUES(?, ?)")
            val = (ctx.guild.id, channel.id)
            await ctx.send(f"Logging channel has been set to {channel.mention}")
        elif result is not None:
            sql = ("UPDATE logs SET channel_id = ? WHERE guild_id = ?")
            val = (channel.id, ctx.guild.id)
            await ctx.send(f"Channel for logs channel has been updated to {channel.mention}")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM logs WHERE guild_id = {message.guild.id}")
        result = cursor.fetchone()
        before = discord.AuditLogEntry.before
        channel = self.bot.get_channel(id=int(result[0]))
        botrole = discord.utils.get(message.author.roles, name='Bots')
        if message.author == self.bot.user:
            return

        if botrole in message.author.roles:
            return
        embed = discord.Embed(timestamp=datetime.datetime.now(tz=datetime.timezone.utc), colour=discord.Colour.from_rgb(237, 42, 45))
        embed.set_author(name=f'{message.author}')
        embed.set_thumbnail(url=f'{message.author.avatar_url}')
        embed.add_field(name=f"Message sent by:",
                        value=f"{message.author.mention} was deleted in {message.channel.mention}", inline=False)
        embed.add_field(name="Deleted message:", value=f"\n\u200b {message.content}", inline=False)
        embed.set_footer(text=f'User ID: {message.author.id}')
        await channel.send(embed=embed)

        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM logs WHERE guild_id = {before.guild.id}")
        result = cursor.fetchone()
        channel = self.bot.get_channel(id=int(result[0]))
        member = discord.Member
        if member.bot:
            return




        embed = discord.Embed(description=f"Message edited by {before.author.mention} in {before.channel}",
                              timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                              colour=discord.Colour.from_rgb(247, 205, 66))
        embed.set_author(name=f'{before.author}', icon_url=f'{before.author.avatar_url}')
        embed.set_thumbnail(url=f'{before.author.avatar_url}')
        embed.add_field(name="Original message", value="\n\u200b" + before.content, inline=False)
        embed.add_field(name="Edited message", value="\n\u200b" + after.content, inline=False)
        embed.add_field(name="\n\u200b", value=f"[Jump to message.]({after.jump_url})")
        embed.set_footer(text=f'User ID: {before.author.id}')
        await channel.send(embed=embed)

        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM logs WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        channel = self.bot.get_channel(id=int(result[0]))
        embed = discord.Embed(title="Member Joined", timestamp=datetime.datetime.now(tz=datetime.timezone.utc), color=discord.Colour.from_rgb(47, 216, 109))
        embed.set_thumbnail(url=f'{member.avatar_url}')
        embed.add_field(name="\n\u200b", value=member.mention + " has joined " + member.guild.name, inline=False)
        embed.add_field(name="Account created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.set_footer(text=f'User ID: {member.id}')
        await channel.send(embed=embed)

        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM logs WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        channel = self.bot.get_channel(id=int(result[0]))
        embed = discord.Embed(title="Member Left", timestamp=datetime.datetime.utcnow(), color=discord.Colour.from_rgb(237, 42, 45))
        embed.set_thumbnail(url=f'{member.avatar_url}')
        embed.add_field(name="\n\u200b", value=member.mention + " has left " + member.guild.name, inline=False)
        embed.set_footer(text=f'User ID: {member.id}')
        await channel.send(embed=embed)

        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_ban(self, user, reason):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM logs WHERE guild_id = {user.guild.id}")
        result = cursor.fetchone()
        channel = self.bot.get_channel(id=int(result[0]))
        embed = discord.Embed(title="Member was banned", timestamp=datetime.datetime.utcnow(), color=discord.Colour.from_rgb(237, 42, 45))
        embed.set_thumbnail(url=f'{user.avatar_url}')
        embed.add_field(name="\n\u200b", value=user.mention + " was banned from" + user.guild.name + f"for {reason}", inline=False)
        embed.set_footer(text=f'User ID: {user.id}')
        await channel.send(embed=embed, reason=reason)

        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_kick(self, user, reason):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM logs WHERE guild_id = {user.guild.id}")
        result = cursor.fetchone()
        channel = self.bot.get_channel(id=int(result[0]))
        embed = discord.Embed(title="Member was kicked", timestamp=datetime.datetime.utcnow(),
                              color=discord.Colour.from_rgb(237, 42, 45))
        embed.set_thumbnail(url=f'{user.avatar_url}')
        embed.add_field(name="\n\u200b", value=user.mention + " was kicked from" + user.guild.name + f"for {reason}",
                        inline=False)
        embed.set_footer(text=f'User ID: {user.id}')
        await channel.send(embed=embed, reason=reason)
        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_unban(self, user):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM logs WHERE guild_id = {user.guild.id}")
        result = cursor.fetchone()
        channel = self.bot.get_channel(id=int(result[0]))
        embed = discord.Embed(title="Member was unbanned", timestamp=datetime.datetime.utcnow(),
                              color=discord.Colour.from_rgb(237, 42, 45))
        embed.set_thumbnail(url=f'{user.avatar_url}')
        embed.add_field(name="\n\u200b", value=user.mention + " was unbanned from" + user.guild.name,
                        inline=False)
        embed.set_footer(text=f'User ID: {user.id}')
        await channel.send(embed=embed)
        db.commit()
        cursor.close()
        db.close()




def setup(bot):
    bot.add_cog(Logging(bot))
    print('logging module loaded')

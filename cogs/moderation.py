import discord
import asyncio
import sqlite3
import typing
from discord.ext import commands

def mute_role(ctx):
    discord.utils.get(ctx.guild.roles, name="Muted")

def member():
    discord.User

def log_channel():
    discord.client.get_channel(785206949192400896)

class Moderation(commands.Cog):
    """Moderation module"""
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permissions for that.")
        if isinstance(error, commands.UserNotFound):
            await ctx.send("User not found.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        """Ban member from guild. Use: <p>ban <member(s)> <reason>"""
        if member == ctx.message.author:
            await ctx.channel.send("You cannot ban yourself!")
            return

        if member == None:
            await ctx.channel.send("Please provide a user!")
            return

        if reason == None:
            reason = "No reason provided."
        message = f"You have been banned from {ctx.guild.name} for {reason}."
        await ctx.guild.ban(member, reason=reason)
        await ctx.channel.send(f"{member} was banned for {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.Member = None, *, reason=None):
        """Unban member from guild. Use: <p>unban <member(s)> <reason>"""
        if member == ctx.message.author:
            await ctx.channel.send("You cannot unban yourself!")
            return

        if member == None:
            await ctx.channel.send("Please provide a user!")
            return

        if reason == None:
            reason = "No reason provided."
        message = f"You have been unbanned from {ctx.guild.name} for {reason}."
        await ctx.guild.unban(member, reason=reason)
        await ctx.channel.send(f"{member} was unbanned.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason=None):
        """Kick member from guild. Use: <p>kick <member(s)> <reason>"""
        if member == ctx.message.author:
            await ctx.channel.send("You cannot kick yourself!")
            return

        if member == None:
            await ctx.channel.send("Please provide a user!")
            return

        if reason == None:
            reason = "No reason provided."
        message = f"You have been kicked from {ctx.guild.name} for {reason}."
        await ctx.guild.kick(member, reason=reason)
        await ctx.channel.send(f"{member} was kicked.")
        await ctx.member.send(message)

    @commands.command(aliases=["purge", "clear", "clean"])
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, amount=2):
        """Delete messages. Use: <p>delete <amount> Aliases:purge, clear, clean"""
        await ctx.channel.purge(limit=amount)
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.channel.send('Deleted {} message(s)'.format(len(deleted)))

    @commands.command()
    @commands.has_role('Mods')
    async def mute(self, ctx, members: discord.Member, mute_minutes: typing.Optional[int] = 0, *, reason: str = "None"):
        """(currently broken)Mute members and optional timer. Use: <p>mute <member(s)> <time> <reason>"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        def field(command, *values):
            cursor.execute(command, tuple(values))

            if (fetch := cursor.fetchone()) is not None:
                return fetch[0]
        if members == ctx.message.author:
            await ctx.channel.send("You cannot limbo yourself!")
            return

        if not members:
            await ctx.send("You need to name someone to mute")
            return

        muted_role = discord.utils.find(ctx.guild.roles, name='Muted')

        for member in members:
            if self.bot.user == member:
                await ctx.send("You can't mute me, I'm an almighty bot")
                return
            if muted_role in member.roles:
                await ctx.send(f"{member.mention} is already muted")
                return

            role_ids = ",".join([str(role.id) for role in member.roles[1:]])

            sql = ("INSERT INTO mutes(guild_id, user_id, roles_ids) VALUES(?, ?, ?)")
            val = (ctx.guild.id, member.id, role_ids)
            await member.edit(roles=[])
            await member.add_roles(muted_role, reason=reason)
            await ctx.send("{0.mention} has been muted by {1.mention} for *{2}*".format(member, ctx.author, reason))
        cursor.execute(sql, val)

        if mute_minutes > 0:
            await asyncio.sleep(mute_minutes * 60)
            for member in members:
                role_ids = field(f"SELECT roles_ids FROM limbo WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
                roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]
                await member.edit(roles=roles)
                cursor.execute(f"DELETE FROM limbo WHERE guild_id = {ctx.guild.id} AND user_id = {member.id}")
                await member.remove_roles(muted_role, reason="time's up ")

        db.commit()
        cursor.close()
        db.close()

    @commands.command()
    @commands.has_role('Mods')
    async def unmute(self, ctx, members: discord.Member, *, reason: str = "None" ):
        """(currently broken)Unmute members. Use: <p>unmute <member(s)> <reason>"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        muterole = discord.utils.find(ctx.guild.roles, name='Muted')
        def field(command, *values):
            cursor.execute(command, tuple(values))

            if (fetch := cursor.fetchone()) is not None:
                return fetch[0]
        if members == ctx.message.author:
            await ctx.channel.send("You cannot unmute yourself!")
            return

        if not members:
            await ctx.send("You need to name someone to mute")
            return

        for member in members:
            if muterole not in member.roles:
                await ctx.send(f"{member.mention} is not muted")
                return

            if muterole in member.roles:
                role_ids = field(f"SELECT roles_ids FROM mutes WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
                roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

                if roles in member.roles:
                    await ctx.send(f"Can't give {member.mention} roles he already has")
                    return

                await member.edit(roles=roles)
                sql = (f"DELETE FROM mutes WHERE guild_id = {ctx.guild.id} AND user_id = {member.id}")
                await member.remove_roles(muterole, reason=reason)
                await ctx.send(f"{member.mention} has been removed from limbo.")

            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()

def setup(bot):
    bot.add_cog(Moderation(bot))
    print('moderation module loaded')
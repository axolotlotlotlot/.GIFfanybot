from datetime import datetime, timedelta
from typing import Optional
from discord import Embed, Member, NotFound, Object
from discord.ext.commands import Greedy, Converter, BadArgument
from discord.utils import find
import discord
import asyncio
import sqlite3
import typing
from discord.ext import commands
from discord.ext.commands import bot_has_permissions


class BannedUser(Converter):
    async def convert(self, ctx, arg):
        if ctx.guild.me.guild_permissions.ban_members:
            if arg.isdigit():
                try:
                    return (await ctx.guild.fetch_ban(Object(id=int(arg)))).user
                except NotFound:
                    raise BadArgument

        banned = [e.user for e in await ctx.guild.bans()]
        if banned:
            if (user := find(lambda u: str(u) == arg, banned)) is not None:
                return user
            else:
                raise BadArgument


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
    async def ban(self, ctx, targets: Greedy[discord.User], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
        else:
            for target in targets:
                if target == ctx.message.author:
                    embed = Embed(description=f":x: You can't ban yourself!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                else:
                    await ctx.guild.ban(discord.Object(id=int(target.id)), reason=reason)
                    embed = Embed(title="Member banned",
                                  colour=0xDD2222,
                                  timestamp=datetime.utcnow())
                    embed.set_thumbnail(url=target.avatar_url)
                    embed.set_footer(text=f'User ID: {target.id}')
                    fields = [("Member", f"{target.mention}", False),
                              ("Reason", reason, False),
                              ("Actioned by", ctx.author.mention, False)]
                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)
                    await ctx.send(embed=embed)
                    #await ctx.send(f"{len(targets)} have been banned")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, targets: Greedy[BannedUser], *, reason: Optional[str] = "No reason provided."):
        """Unban member from guild. Use: <p>unban <member(s)> <reason>"""
        if not len(targets):
            await ctx.send("Please provide member(s)")

        else:
            for target in targets:
                if target == ctx.message.author:
                    await ctx.channel.send("You cannot unban yourself!")
                    return
                await ctx.guild.unban(target, reason=reason)
                embed = Embed(title="Member unbanned",
                              colour=0xDD2222,
                              timestamp=datetime.utcnow())
                embed.set_thumbnail(url=target.avatar_url)
                embed.set_footer(text=f'User ID: {target.id}')
                fields = [("Member", f"{target.mention}", False),
                          ("Reason", reason, False),
                          ("Actioned by", ctx.author.mention, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                await ctx.send(embed=embed)

    @commands.command()
    @bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
        if not len(targets):
            await ctx.send("Please provide member(s)")
        else:
            for target in targets:
                if target == ctx.message.author:
                    await ctx.channel.send("You cannot ban yourself!")
                    return
                if (ctx.message.guild.me.top_role.position > target.top_role.position
                        and not target.guild_permissions.administrator):
                    await target.kick(reason=reason)
                    embed = Embed(title="Member kicked",
                                  colour=0xDD2222,
                                  timestamp=datetime.utcnow())
                    embed.set_thumbnail(url=target.avatar_url)
                    embed.set_footer(text=f'User ID: {target.id}')
                    fields = [("Member", f"{target.mention}", False),
                              ("Reason", reason, False),
                              ("Actioned by", ctx.author.mention, False)]
                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)
                    await ctx.send(embed=embed)
                    await ctx.send(f"{len(targets)} have been kicked")

    @commands.command(aliases=["purge", "clear", "clean"])
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, amount=2):
        """Delete messages. Use: <p>delete <amount> Aliases:purge, clear, clean"""
        deleted = await ctx.channel.purge(limit=amount)
        async with ctx.typing():
            await asyncio.sleep(0.5)
        await ctx.channel.send('Deleted {} messages'.format(len(deleted)))

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
                role_ids = field(
                    f"SELECT roles_ids FROM limbo WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
                roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]
                await member.edit(roles=roles)
                cursor.execute(f"DELETE FROM limbo WHERE guild_id = {ctx.guild.id} AND user_id = {member.id}")
                await member.remove_roles(muted_role, reason="time's up ")

        db.commit()
        cursor.close()
        db.close()

    @commands.command()
    @commands.has_role('Mods')
    async def unmute(self, ctx, members: discord.Member, *, reason: str = "None"):
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
                role_ids = field(
                    f"SELECT roles_ids FROM mutes WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
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

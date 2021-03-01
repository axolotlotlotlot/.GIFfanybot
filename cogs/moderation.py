from datetime import datetime, timedelta
from typing import Optional
import dataset
import sqlite3
from discord import Embed, Member, NotFound, Object
from discord.ext.commands import Greedy, Converter, BadArgument
from discord.utils import find
from random import choice
import discord
import asyncio
from discord.ext import tasks, commands
from discord.ext.commands import bot_has_permissions
import time
from stuf import stuf


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
        self.unmute_task.start()

    @commands.command()
    @bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, targets: Greedy[discord.User], *, reason: Optional[str] = "No reason provided."):
        """lets me be ban members frm the guild"""
        if not len(targets):
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return
        else:
            for target in targets:
                if target == ctx.message.author:
                    embed = Embed(description=f":x: You can't ban yourself!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                guild = self.bot.get_guild(ctx.guild.id)
                member = guild.get_member(target.id)
                if target == member:
                    if ctx.message.author.top_role.position == member.top_role.position:
                        embed = Embed(description=f":x: You can't ban people with the same rank as you!",
                                      color=0xDD2222)
                        await ctx.send(embed=embed)
                        return

                    if ctx.message.author.top_role.position < member.top_role.position:
                        embed = Embed(description=f":x: You can't ban people with higher rank then you!",
                                      color=0xDD2222)
                        await ctx.send(embed=embed)
                        return

                    if ctx.message.author.top_role.position > member.top_role.position:
                        db = dataset.connect('sqlite:///journal3.db', row_type=stuf)
                        db.begin()
                        table = db['strikes']
                        if len(table) == 0:
                            sid = 1
                        else:
                            sid = len(table) + 1
                        table.insert(dict(strikeid=sid, guildid=ctx.guild.id, user=member.id, action="Ban", reason=reason))
                        db.commit()
                        await ctx.guild.ban(discord.Object(id=int(member.id)), reason=reason, delete_message_days=0)
                        embed = discord.Embed(description=f":white_check_mark: {member.mention} **was banned** for {reason} \n**Member ID:** {member.id} \n**Actioned by:** {ctx.author.mention}",
                                              colour=discord.Colour.from_rgb(119, 178, 85),
                                              timestamp=datetime.utcnow()

                        )
                        embed.set_thumbnail(url=member.avatar_url)
                        await ctx.send(embed=embed)
                        return
                else:
                    db = dataset.connect('sqlite:///journal3.db', row_type=stuf)
                    db.begin()
                    table = db['strikes']
                    if len(table) == 0:
                        sid = 1
                    else:
                        sid = len(table) + 1
                    table.insert(dict(strikeid=sid, guildid=ctx.guild.id, user=target.id, action="Ban", reason=reason))
                    db.commit()
                    await ctx.guild.ban(discord.Object(id=int(target.id)), reason=reason, delete_message_days=0)
                    embed = discord.Embed(description=f":white_check_mark: {target.mention} **was banned** for {reason} \n**User ID:** {target.id} \n**Actioned by:** {ctx.author.mention}",
                                          colour=discord.Colour.from_rgb(119, 178, 85),
                                          timestamp=datetime.utcnow()

                    )
                    embed.set_thumbnail(url=target.avatar_url)
                    await ctx.send(embed=embed)




    @commands.command()
    @bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, targets: Greedy[BannedUser], *, reason: Optional[str] = "No reason provided."):
        """Unban member from guild. Use: <p>unban <member(s)> <reason>"""
        if not len(targets):
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        else:
            for target in targets:
                if target == ctx.message.author:
                    embed = Embed(description=f":x: You can't unban yourself!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                db = dataset.connect('sqlite:///journal3.db', row_type=stuf)
                db.begin()
                table = db['strikes']
                if len(table) == 0:
                    sid = 1
                else:
                    sid = len(table) + 1
                table.insert(dict(strikeid=sid, guildid=ctx.guild.id, user=member.id, action="Unban", reason=reason))
                db.commit()
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
        """lets me kick members from the guild"""
        if not len(targets):
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
        else:
            for target in targets:
                if target == ctx.message.author:
                    embed = Embed(description=f":x: You can't kick yourself!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                if ctx.message.author.top_role.position == member.top_role.position:
                    embed = Embed(description=f":x: You can't kick people with the same rank as you!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

                if ctx.message.author.top_role.position < member.top_role.position:
                    embed = Embed(description=f":x: You can't kick people with higher rank then you!",
                                  color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

                if ctx.message.author.top_role.position > member.top_role.position:
                    db = dataset.connect('sqlite:///journal3.db', row_type=stuf)
                    db.begin()
                    table = db['strikes']
                    if len(table) == 0:
                        sid = 1
                    else:
                        sid = len(table) + 1
                    table.insert(dict(strikeid=sid, guildid=ctx.guild.id, user=member.id, action="Kick", reason=reason))
                    db.commit()
                    await target.kick(reason=reason)
                    embed = discord.Embed(description=f":white_check_mark: {member.mention} **was kicked** for {reason} \n**Member ID:** {member.id} \n**Actioned by:** {ctx.author.mention}",
                                          colour=discord.Colour.from_rgb(119, 178, 85),
                                          timestamp=datetime.utcnow()

                    )
                    embed.set_thumbnail(url=member.avatar_url)
                    await ctx.send(embed=embed)

    @commands.command(aliases=["purge", "clear", "clean", "remove"])
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, amount=0):
        """Delete messages. Use: <p>delete <amount> Aliases:purge, clear, clean"""
        if amount == 0:
            embed = Embed(description=f":x: Please provide amount of messages to delete",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return
        deleted = await ctx.channel.purge(limit=amount)
        async with ctx.typing():
            await asyncio.sleep(0.5)
        embed = discord.Embed(description=":white_check_mark: Deleted {0} messages".format(len(deleted)),
                              timestamp=datetime.utcnow(),
                              color=0x77B255)
        await ctx.send(embed=embed)

    def channelslist(guild):
        msg = ''
        for g in guild.channels:
            msg = msg + f"'{g.id}'" + " , "
        return msg

    @commands.command(aliases=["udelete", "upurge", "uclear", "uclean", "uremove", "userpurge", "userclear", "userclean", "userremove"])
    @commands.has_permissions(manage_messages=True)
    async def userdelete(self, ctx, user: discord.User=None, amount=300):
        """Delete all messages of an user."""
        msg = ''
        for g in ctx.guild.text_channels:
            msg = msg + f"{g.name}" + ","

        #print(msg.split(","))
        channels = [channel for channel in ctx.guild.text_channels if channel.name in msg.split(",")]
        #channel = [ctx.guild.get_channel(int(id_)) for id_ in msg.split(",") if len(id_)]

        if user == None:
            embed = Embed(description=f":x: Please provide a user",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        elif amount == 0:
            embed = Embed(description=f":x: Please provide amount of messages to delete",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        def check(msg):
            return msg.author.id == user.id

        await ctx.message.delete()
        for channel in channels:
            #print(channel)
            deleted = await channel.purge(limit=amount, check=check, before=None)
            if len(deleted) > 0:
                async with ctx.typing():
                    await asyncio.sleep(0.5)
                embed = discord.Embed(description=":white_check_mark: Deleted {0} messages in {1} from {2}".format(len(deleted), channel.mention, user.mention),
                                      timestamp=datetime.utcnow(),
                                      color=0x77B255)
                embed.set_footer(text=f"Auctioned by: {ctx.author}")
                await ctx.send(embed=embed)

    @commands.command()
    @bot_has_permissions(manage_roles=True)
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: Member, time: int=None, type=None, *, reason="No reason provided."):
        """lets me temporarily mute members"""
        db = dataset.connect('sqlite:///journal3.db', row_type=stuf)
        db.begin()
        table = db['strikes']
        mutetable = db['mutes']
        muterole = discord.utils.get(ctx.guild.roles, name="Muted")
        member_roles = ",".join([str(role.id) for role in member.roles[1:]])
        def mutes(guild):
            db = dataset.connect('sqlite:///journal3.db', row_type=stuf)
            db.begin()
            mutes = db.query('SELECT user FROM mutes WHERE guildid = {0}'.format(guild.id))
            for m in mutes:
                muted = m.user
                return muted
            return None
        muted = mutes(ctx.guild)

        if len(table) == 0:
            sid = 1
        else:
            sid = len(table) + 1

        if member == None:
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if member is ctx.author:
            embed = Embed(description=f":x: You can't mute yourself",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if time is None:
            embed = Embed(description=f":x: Please provide mute time",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if ctx.message.author.top_role.position == member.top_role.position:
            embed = Embed(description=f":x: You can't mute people with the same rank as you!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if ctx.message.author.top_role.position < member.top_role.position:
            embed = Embed(description=f":x: You can't mute people with higher rank then you!",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if ctx.message.author.top_role.position > member.top_role.position:
            d = ['d', 'day', 'days']
            h = ['h', 'hour', 'hours']
            m = ['m', 'min', 'minute', 'minutes']

        if type.lower() in d:
            if member.id == muted:
                oldendtime = mutetable.distinct('endtime', guildid=ctx.guild.id, user=member.id)
                for oet in oldendtime:
                    oldtime = oet.endtime
                newtime = oldtime + timedelta(days=int(time))
                mutetable.update(dict(guildid=ctx.guild.id, user=member.id, endtime=newtime), ['guildid', 'user'])
                db.commit()
                embed = discord.Embed(title="Mute time updated",
                                      description=member.mention + " was muted. \nFor: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"+ {time} more day(s)",
                                      timestamp=datetime.utcnow(),
                                      color=discord.Colour.from_rgb(255, 198, 243))
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)
            else:
                endtime = datetime.utcnow() + timedelta(days=int(time))
                table.insert(dict(strikeid=sid, guildid=ctx.guild.id, user=member.id, action="Mute", reason=reason))
                mutetable.insert(dict(guildid=ctx.guild.id, user=member.id, roles=member_roles, starttime=datetime.utcnow(), endtime=endtime))
                db.commit()
                await member.edit(roles=[])
                await member.add_roles(muterole)
                embed = discord.Embed(title="Member was muted",
                                      description=member.mention + " was muted. \nFor: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"{time} day(s)",
                                      timestamp=datetime.utcnow(),
                                      color=discord.Colour.from_rgb(255, 198, 243))
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)

        elif type.lower() in h:
            if member.id == muted:
                oldendtime = mutetable.distinct('endtime', guildid=ctx.guild.id, user=member.id)
                for oet in oldendtime:
                    oldtime = oet.endtime
                newtime = oldtime + timedelta(hours=int(time))
                mutetable.update(dict(guildid=ctx.guild.id, user=member.id, endtime=newtime), ['guildid', 'user'])
                db.commit()
                embed = discord.Embed(title="Mute time updated",
                                      description=member.mention + " was muted. \nFor: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"+ {time} more hour(s)",
                                      timestamp=datetime.utcnow(),
                                      color=discord.Colour.from_rgb(255, 198, 243))
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)
            else:
                endtime = datetime.utcnow() + timedelta(hours=int(time))
                table.insert(dict(strikeid=sid, guildid=ctx.guild.id, user=member.id, action="Mute", reason=reason))
                mutetable.insert(dict(guildid=ctx.guild.id, user=member.id, roles=member_roles, starttime=datetime.utcnow(), endtime=endtime))
                db.commit()
                await member.edit(roles=[])
                await member.add_roles(muterole)
                embed = discord.Embed(title="Member was muted",
                                      description=member.mention + " was muted. \nFor: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"{time} hour(s)",
                                      timestamp=datetime.utcnow(),
                                      color=discord.Colour.from_rgb(255, 198, 243))
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)

        elif type.lower() in m:
            if member.id == muted:
                oldendtime = mutetable.distinct('endtime', guildid=ctx.guild.id, user=member.id)
                for oet in oldendtime:
                    oldtime = oet.endtime
                newtime = oldtime + timedelta(minutes=int(time))
                mutetable.update(dict(guildid=ctx.guild.id, user=member.id, endtime=newtime), ['guildid', 'user'])
                db.commit()
                embed = discord.Embed(title="Mute time updated",
                                      description=member.mention + " was muted. \nReason: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"+ {time} more minute(s)",
                                      timestamp=datetime.utcnow(),
                                      color=discord.Colour.from_rgb(255, 198, 243))
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)
            else:
                endtime = datetime.utcnow() + timedelta(minutes=int(time))
                table.insert(dict(strikeid=sid, guildid=ctx.guild.id, user=member.id, action="Mute", reason=reason))
                mutetable.insert(dict(guildid=ctx.guild.id, user=member.id, roles=member_roles, starttime=datetime.utcnow(), endtime=endtime))
                db.commit()
                await member.edit(roles=[])
                await member.add_roles(muterole)
                embed = discord.Embed(title="Member was muted",
                                      description=member.mention + " was muted. \nReason: " + reason + "\nBy: " + ctx.message.author.mention + "\nDuration: " + f"{time} minute(s)",
                                      timestamp=datetime.utcnow(),
                                      color=discord.Colour.from_rgb(255, 198, 243))
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.set_footer(text=f'User ID: {member.id}')
                await ctx.send(embed=embed)

        elif type.lower() not in m or d or h:
            await ctx.message.delete()
            embed = Embed(description=f":x: Time type not supported. You can use: ['d', 'day', 'days'], ['h', 'hour', 'hours'], ['m', 'min', 'minute', 'minutes'].",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

    @commands.command()
    @bot_has_permissions(manage_roles=True)
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: Member=None, *, reason: Optional[str] = "No reason provided."):
        """lets me unmute muted members"""
        if member is None:
            embed = Embed(description=f":x: Please provide a member",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['mutes']
        muterole = discord.utils.get(ctx.guild.roles, name="Muted")
        member_role_ids = [y.id for y in member.roles]
        userids = table.distinct('user', guildid=ctx.guild.id, user=member.id)
        for u in userids:
            uid = u['user']
        if (muterole.id in member_role_ids) and (member.id == uid):
            roleids = table.distinct('roles', guildid=ctx.guild.id, user=member.id)
            for r in roleids:
                rid = r['roles']
            roles = [ctx.guild.get_role(int(id_)) for id_ in rid.split(",") if len(id_)]

            await member.edit(roles=roles)
            embed = discord.Embed(title="Member was unmuted",
                                  description=member.mention + " was unmuted. \nReason: " + reason + "\nBy: " + ctx.message.author.mention,
                                  timestamp=datetime.utcnow(),
                                  color=discord.Colour.from_rgb(255, 198, 243))
            embed.set_thumbnail(url=f'{member.avatar_url}')
            embed.set_footer(text=f'User ID: {member.id}')
            await ctx.send(embed=embed)

            table.delete(guildid=ctx.guild.id, user=member.id)
            db.commit()
        else:
            embed = Embed(description=f":x: Member not muted",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

    @tasks.loop(minutes=1)
    async def unmute_task(self):
        db = dataset.connect('sqlite:///journal3.db', row_type=stuf)
        db.begin()
        table = db['mutes']
        endtime = table.distinct('endtime', endtime={'<=':f'{datetime.utcnow()}'})
        for e in endtime:
            users = table.distinct('user', endtime=e.endtime)
            for u in users:
                user = u.user
                for guilds in self.bot.guilds:
                    for members in guilds.members:
                        if user == members.id:
                            for role in members.roles:
                                if "Muted" in role.name:
                                    logchannel = discord.utils.get(guilds.channels, name="mod-log")
                                    roleids = table.distinct('roles', user=members.id, guildid=guilds.id, endtime=e.endtime)
                                    for r in roleids:
                                        rid = r['roles']
                                    roles = [guilds.get_role(int(id_)) for id_ in rid.split(",") if len(id_)]
                                    await members.edit(roles=roles)
                                    embed = discord.Embed(title="Member was unmuted",
                                                          description=members.mention + " was unmuted. \nReason: Mute time expired.",
                                                          timestamp=datetime.utcnow(),
                                                          color=discord.Colour.from_rgb(255, 198, 243))
                                    embed.set_thumbnail(url=f'{members.avatar_url}')
                                    embed.set_footer(text=f'User ID: {members.id}')
                                    await logchannel.send(embed=embed)

                                    table.delete(guildid=guilds.id, user=members.id, endtime=e.endtime)
                                    db.commit()

def setup(bot):
    bot.add_cog(Moderation(bot))
    print('moderation module loaded')

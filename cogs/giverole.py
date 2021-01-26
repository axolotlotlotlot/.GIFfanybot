import asyncio
import re
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import discord
import dataset
from discord import Member, Embed
from discord.ext import commands
from discord.ext.commands import Greedy, CommandNotFound

def findroleid(roleName, guild):
    roles = guild.roles
    for i in roles:
        if i.name == roleName:
            return i.id
    return None


class giverole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def giveyou(self, ctx, targets: Greedy[Member], Name=None):
        """This command allows mods who normally do not have permissions to assign roles, to assign preset roles to users. Assigning a giveyou to a member who already has the role will remove it.
           Use: .giveyou <member(s)> <name>"""
        db1 = sqlite3.connect('journal3.db')
        cursor = db1.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        results = field("SELECT name FROM giveyou WHERE guildid = ? AND name = ?", ctx.guild.id, Name)
        roleids = field("SELECT roleid FROM giveyou WHERE guildid = ? AND name = ?", ctx.guild.id, Name)
        roles = discord.utils.get(ctx.guild.roles, id=roleids)

        if not len(targets):
            embed = Embed(
                description=":x: Please provide member(s)",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if Name == None:
            embed = Embed(
                description=":x: Please provide a giveyou name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if results != Name:
            embed = Embed(
                description=f":x: Couldn't find **{Name}** in giveyou database",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return
        if results == Name:
            for target in targets:
                if roles in target.roles:
                    await target.remove_roles(roles)
                    embed = discord.Embed(
                        description=f":white_check_mark: I have removed **{Name}** from {target.mention}",
                        timestamp=datetime.utcnow(),
                        color=0x77B255)
                    embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                    await ctx.send(embed=embed)
                elif roles not in target.roles:
                    await target.add_roles(roles)
                    embed = discord.Embed(
                        description=f":white_check_mark: I have assigned **{Name}** to {target.mention}",
                        timestamp=datetime.utcnow(),
                        color=0x77B255)
                    embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                    await ctx.send(embed=embed)

    @giveyou.command(aliases=['add'])
    @commands.has_permissions(administrator=True)
    async def create(self, ctx, name=None, *, roleName=None):
        """(Admin only)Create giveyous. Use: .giveyou create <name> <role(case sensitive)>"""
        if name == None:
            embed = Embed(
                description=":x: Please provide a role",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if roleName == None:
            embed = Embed(
                description=":x: Please provide a role",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        roleID = findroleid(roleName, ctx.guild)
        if roleID == None:
            embed = Embed(
                description=":x: I couldn't find a role with the name **{0}**. Are you sure it exists?".format(
                    roleName),
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        rolenames = field("SELECT name FROM giveyou WHERE guildid = ? AND rolename = ?", ctx.guild.id, roleName)

        if name == rolenames:
            embed = Embed(description=f":x: giveyou with the name **{name}** already exists",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if roleName != rolenames:
            db = dataset.connect('sqlite:///journal3.db')
            db.begin()
            table = db['giveyou']
            table.insert(dict(guildid=ctx.guild.id, name=name, rolename=roleName, roleid=roleID))
            db.commit()
            embed = discord.Embed(description=f":white_check_mark: giveyou **{name}** created",
                                  timestamp=datetime.utcnow(),
                                  color=0x77B255)
            embed.set_footer(text=f'created by: {ctx.author} / {ctx.author.id}')
            await ctx.send(embed=embed)
        db.commit()
        cursor.close()
        db.close()

    @giveyou.command(aliases=['remove'])
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, name=None):
        """(Admin only)Remove giveyous. Use: .giveyou remove <name>"""
        if name == None:
            embed = Embed(
                description=":x: Please provide a giveyou",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['giveyou']
        rolenames = table.find(guildid=ctx.guild.id, name=name)
        for rolename in rolenames:
            if name == rolename['name']:
                table.delete(guildid=ctx.guild.id, name=name)
                db.commit()
                embed = discord.Embed(description=f":white_check_mark: giveyou **{name}** removed",
                                      timestamp=datetime.utcnow(),
                                      color=0x77B255)
                embed.set_footer(text=f'removed by: {ctx.author} / {ctx.author.id}')
                await ctx.send(embed=embed)
            else:
                embed = Embed(description=f":x: I couldn't find a giveyou with the name **{name}**",
                              color=0xDD2222)
                await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def giveme(self, ctx, *, Name=None, member: discord.Member = None):
        if member == None:
            member = ctx.message.author

        elif member != None:
            member = ctx.message.author

        db1 = sqlite3.connect('journal3.db')
        cursor = db1.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        results = field("SELECT name FROM giveme WHERE guildid = ? AND name = ?", ctx.guild.id, Name)
        roleids = field("SELECT roleid FROM giveme WHERE guildid = ? AND name = ?", ctx.guild.id, Name)
        rankids = field("SELECT rankid FROM giveme WHERE guildid = ? AND name = ?", ctx.guild.id, Name)
        roles = discord.utils.get(ctx.guild.roles, id=roleids)
        rank = discord.utils.get(ctx.guild.roles, id=rankids)

        if Name == None:
            embed = Embed(
                description=":x: Please provide a giveme name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if results != Name:
            embed = Embed(
                description=f":x: Couldn't find **{Name}** in giveme database",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if rank in member.roles or rank == None:
            if results == Name:
                if roles in member.roles:
                    await member.remove_roles(roles)
                    embed = discord.Embed(
                        description=f":white_check_mark: I have removed **{Name}** from {member.mention}",
                        timestamp=datetime.utcnow(),
                        color=0x77B255)
                    embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                    await ctx.send(embed=embed)
                elif roles not in member.roles:
                    await member.add_roles(roles)
                    embed = discord.Embed(
                        description=f":white_check_mark: I have assigned **{Name}** to {member.mention}",
                        timestamp=datetime.utcnow(),
                        color=0x77B255)
                    embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                    await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f":x: You don't have rank required for this giveme",
                color=0xDD2222)
            await ctx.send(embed=embed)

        db1.commit()
        cursor.close()
        db1.close()

    @giveme.command(aliases=['add'])
    @commands.has_permissions(administrator=True)
    async def create(self, ctx, name=None, roleName: Optional[str]=None, *, rankName=None):

        if name == None:
            embed = Embed(
                description=":x: Please provide a role",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if roleName == None:
            embed = Embed(
                description=":x: Please provide a role",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        roleID = findroleid(roleName, ctx.guild)
        if roleID == None:
            embed = Embed(
                description=":x: I couldn't find a role with the name **{0}**. Are you sure it exists?".format(
                    roleName),
                color=0xDD2222)
            await ctx.send(embed=embed)
            return
        if rankName != None:
            def findrankid(rankName, guild):
                roles = guild.roles
                for i in roles:
                    if i.name == rankName:
                        return i.id
                    elif i.id == rankName:
                        return i.id
                return None

            rankID = findrankid(rankName, ctx.guild)
            if rankID == None:
                embed = Embed(
                    description=":x: I couldn't find a rank with the name **{0}**. Are you sure it exists?".format(
                        rankName),
                    color=0xDD2222)
                await ctx.send(embed=embed)
                return
        else:
            rankID = None

        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        rolenames = field("SELECT name FROM giveme WHERE guildid = ? AND rolename = ?", ctx.guild.id, roleName)

        if name == rolenames:
            embed = Embed(description=f":x: giveme with the name **{name}** already exists",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if roleName != rolenames:
            db = dataset.connect('sqlite:///journal3.db')
            db.begin()
            table = db['giveme']
            table.insert(dict(guildid=ctx.guild.id, rankname=rankName, rankid=rankID, name=name, rolename=roleName, roleid=roleID))
            db.commit()
            embed = discord.Embed(description=f":white_check_mark: giveme **{name}** created \n Requirements:{rankName}",
                                  timestamp=datetime.utcnow(),
                                  color=0x77B255)
            embed.set_footer(text=f'created by: {ctx.author} / {ctx.author.id}')
            await ctx.send(embed=embed)
        db.commit()
        cursor.close()
        db.close()

    @giveme.command(aliases=['remove'])
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, name=None):
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['giveme']

        if name == None:
            embed = Embed(
                description=":x: Please provide a giveme name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        Names = ''
        for i in db['giveme']:
            if i['guildid'] == ctx.guild.id:
                Names = Names + f"{i['name']}"
        if i['guildid'] == ctx.guild.id:
            p = set(str(name)) & set(str(Names))
            if p:
                table.delete(guildid=ctx.guild.id, name=name)
                db.commit()
                embed = discord.Embed(description=f":white_check_mark: giveme **{name}** removed",
                                      timestamp=datetime.utcnow(),
                                      color=0x77B255)
                embed.set_footer(text=f'removed by: {ctx.author} / {ctx.author.id}')
                await ctx.send(embed=embed)
            else:
                embed = Embed(description=f":x: I couldn't find a giveme with the name **{name}**",
                              color=0xDD2222)
                await ctx.send(embed=embed)

    @commands.group()
    @commands.has_permissions(administrator=True)
    async def role(self, ctx, member: discord.Member = None, *, roleName=None):
        if member == None:
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
        else:
            if roleName == None:
                embed = Embed(
                    description=":x: Please provide a role",
                    color=0xDD2222)
                await ctx.send(embed=embed)
                return

            roleID = findroleid(roleName, ctx.guild)
            if roleID == None:
                embed = Embed(
                    description=":x: I couldn't find a role with the name **{0}**. Are you sure it exists?".format(
                        roleName),
                    color=0xDD2222)
                await ctx.send(embed=embed)
                return
            roles = discord.utils.get(ctx.guild.roles, id=roleID)
            if roles in member.roles:
                await member.remove_roles(roles)
                embed = discord.Embed(
                    description=f":white_check_mark: I have removed **{roles}** from {member.mention}",
                    timestamp=datetime.utcnow(),
                    color=0x77B255)
                embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                await ctx.send(embed=embed)
            elif roles not in member.roles:
                await member.add_roles(roles)
                embed = discord.Embed(
                    description=f":white_check_mark: I have assigned **{roles}** to {member.mention}",
                    timestamp=datetime.utcnow(),
                    color=0x77B255)
                embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                await ctx.send(embed=embed)

    @role.command()
    async def add(self, ctx, members: Greedy[discord.Member], *, roleName=None):
        if not len(members):
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
        else:
            for member in members:
                if roleName == None:
                    embed = Embed(
                        description=":x: Please provide a role",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

                roleID = findroleid(roleName, ctx.guild)
                if roleID == None:
                    embed = Embed(
                        description=":x: I couldn't find a role with the name **{0}**. Are you sure it exists?".format(
                            roleName),
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                roles = discord.utils.get(ctx.guild.roles, id=roleID)
                if roles in member.roles:
                    if roles in member.roles:
                        embed = Embed(
                            description=f":x: User {member.mention} already has that role",
                            color=0xDD2222)
                        await ctx.send(embed=embed)
                    elif roles not in member.roles:
                        await member.add_roles(roles)
                        embed = discord.Embed(
                            description=f":white_check_mark: I have assigned **{roles}** to {member.mention}",
                            timestamp=datetime.utcnow(),
                            color=0x77B255)
                        embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                        await ctx.send(embed=embed)

    @role.command()
    async def remove(self, ctx, members: Greedy[discord.Member], *, roleName=None):
        if not len(members):
            embed = Embed(description=f":x: Please provide member(s)",
                          color=0xDD2222)
            await ctx.send(embed=embed)
        else:
            for member in members:
                if roleName == None:
                    embed = Embed(
                        description=":x: Please provide a role",
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return

                roleID = findroleid(roleName, ctx.guild)
                if roleID == None:
                    embed = Embed(
                        description=":x: I couldn't find a role with the name **{0}**. Are you sure it exists?".format(
                            roleName),
                        color=0xDD2222)
                    await ctx.send(embed=embed)
                    return
                roles = discord.utils.get(ctx.guild.roles, id=roleID)
                if roles in member.roles:
                    await member.remove_roles(roles)
                    embed = discord.Embed(
                        description=f":white_check_mark: I have removed **{roles}** from {member.mention}",
                        timestamp=datetime.utcnow(),
                        color=0x77B255)
                    embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                    await ctx.send(embed=embed)
                elif roles not in member.roles:
                    embed = Embed(
                        description=f":x: User {member.mention} doesn't have that role",
                        color=0xDD2222)
                    await ctx.send(embed=embed)



    @commands.group(aliases=['colorme'],invoke_without_command=True)
    async def colourme(self, ctx, *, Name=None, member: discord.Member = None):
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['colourme']

        if member is None or member is not None:
            member = ctx.author

        if Name is None:
            embed = Embed(
                description=f":x: Please provide colourme name",
                color=0xDD2222)
            await ctx.send(embed=embed)

        member_ids = ",".join([str(role.id) for role in member.roles[1:]])
        member_roles = member_ids.split(',')


        roles = table.distinct('roleid', guildid=ctx.guild.id)
        msgr = ''
        for r in roles:
            msgr = msgr + f"{int(r['roleid'])}" + ','
            clrole = msgr.split(',')

        p = set(clrole) & set(member_roles)

        names = table.distinct('name', guildid=ctx.guild.id, name=Name)
        roleids = table.distinct('roleid', guildid=ctx.guild.id, name=Name)
        rankids = table.distinct('rankid', guildid=ctx.guild.id, name=Name)
        for n in names:
            name = n['name']
        for rankid in rankids:
            rank = discord.utils.get(ctx.guild.roles, id=rankid['rankid'])
        for roleid in roleids:
            roles = discord.utils.get(ctx.guild.roles, id=roleid['roleid'])

        msg = ''
        for i in db['colourme']:
            if i['guildid'] == ctx.guild.id:
                msg = msg + f"{int(i['roleid'])}" + ','
        croles = msg.split(',')

        if name != Name:
            embed = Embed(
                description=f":x: Couldn't find **{Name}** in colourme database",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if rank in member.roles or rank == None:
            if name == Name:

                if roles in member.roles:
                    await member.remove_roles(roles)
                    embed = discord.Embed(
                        description=f":white_check_mark: I have removed {roles.mention} from {member.mention}",
                        timestamp=datetime.utcnow(),
                        color=0x77B255)
                    embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                    await ctx.send(embed=embed)
                    return

                if roles not in member.roles:
                    if p:
                        crole_match = [c for c in croles if c in member_roles]
                        cc = str(crole_match).strip("[]'")
                        crs = discord.utils.get(ctx.guild.roles, id=int(cc))
                        await member.remove_roles(crs)
                        embed = discord.Embed(
                            description=f":white_check_mark: I have removed {crs.mention} from {member.mention}",
                            timestamp=datetime.utcnow(),
                            color=0x77B255)
                        embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                        await ctx.send(embed=embed)
                        await asyncio.sleep(0.5)
                        await member.add_roles(roles)
                        embed = discord.Embed(
                            description=f":white_check_mark: I have assigned {roles.mention} to {member.mention}",
                            timestamp=datetime.utcnow(),
                            color=0x77B255)
                        embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                        await ctx.send(embed=embed)
                    else:
                        await member.add_roles(roles)
                        embed = discord.Embed(
                            description=f":white_check_mark: I have assigned {roles.mention} to {member.mention}",
                            timestamp=datetime.utcnow(),
                            color=0x77B255)
                        embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                        await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f":x: You don't have rank required for this colourme",
                color=0xDD2222)
            await ctx.send(embed=embed)

    @colourme.command(aliases=['add'])
    @commands.has_permissions(administrator=True)
    async def create(self, ctx, name=None, roleName: Optional[str] = None, *, rankName=None):

        if name == None:
            embed = Embed(
                description=":x: Please provide a role",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if roleName == None:
            embed = Embed(
                description=":x: Please provide a role",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        roleID = findroleid(roleName, ctx.guild)
        if roleID == None:
            embed = Embed(
                description=":x: I couldn't find a role with the name **{0}**. Are you sure it exists?".format(
                    roleName),
                color=0xDD2222)
            await ctx.send(embed=embed)
            return
        if rankName != None:
            def findrankid(rankName, guild):
                roles = guild.roles
                for i in roles:
                    if i.name == rankName:
                        return i.id
                return None

            rankID = findrankid(rankName, ctx.guild)
            if rankID == None:
                embed = Embed(
                    description=":x: I couldn't find a rank with the name **{0}**. Are you sure it exists?".format(
                        rankName),
                    color=0xDD2222)
                await ctx.send(embed=embed)
                return
        else:
            rankID = None

        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        rolenames = field("SELECT name FROM colourme WHERE guildid = ? AND rolename = ?", ctx.guild.id, roleName)

        if name == rolenames:
            embed = Embed(description=f":x: colourme with the name **{name}** already exists",
                          color=0xDD2222)
            await ctx.send(embed=embed)
            return

        if roleName != rolenames:
            db = dataset.connect('sqlite:///journal3.db')
            db.begin()
            table = db['colourme']
            table.insert(dict(guildid=ctx.guild.id, rankname=rankName, rankid=rankID, name=name, rolename=roleName,
                              roleid=roleID))
            db.commit()
            embed = discord.Embed(
                description=f":white_check_mark: colourme **{name}** created \n Requirements:{rankName}",
                timestamp=datetime.utcnow(),
                color=0x77B255)
            embed.set_footer(text=f'created by: {ctx.author} / {ctx.author.id}')
            await ctx.send(embed=embed)
        db.commit()
        cursor.close()
        db.close()

    @colourme.command(aliases=['remove'])
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, name=None):
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['colourme']

        if name == None:
            embed = Embed(
                description=":x: Please provide a colourme name",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        Names = ''
        for i in db['colourme']:
            if i['guildid'] == ctx.guild.id:
                Names = Names + f"{i['name']}"
        if i['guildid'] == ctx.guild.id:
            p = set(str(name)) & set(str(Names))
            if p:
                table.delete(guildid=ctx.guild.id, name=name)
                db.commit()
                embed = discord.Embed(description=f":white_check_mark: colourme **{name}** removed",
                                      timestamp=datetime.utcnow(),
                                      color=0x77B255)
                embed.set_footer(text=f'removed by: {ctx.author} / {ctx.author.id}')
                await ctx.send(embed=embed)
            else:
                embed = Embed(description=f":x: I couldn't find a colourme with the name **{name}**",
                              color=0xDD2222)
                await ctx.send(embed=embed)

    @colourme.command()
    async def list(self, ctx):
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        msg = ''
        for i in db['colourme']:
            if i['guildid'] == ctx.guild.id:
                msg = msg + '**' + f"{i['name']}" + '** \n'
        if i['guildid'] == ctx.guild.id:
            await ctx.send(msg)
        else:
            await ctx.send(" No colourmes for this server found")

def setup(bot):
    bot.add_cog(giverole(bot))
    print('giverole module loaded')

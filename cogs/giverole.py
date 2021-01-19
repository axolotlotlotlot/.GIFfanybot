import sqlite3
from datetime import datetime, timedelta
import discord
import dataset
from discord import Member
from discord.ext import commands
from discord.ext.commands import Greedy
from discord import Embed


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
                    embed = discord.Embed(description=f":white_check_mark: I have removed **{Name}** from {target.mention}",
                                          timestamp=datetime.utcnow(),
                                          color=0x77B255)
                    embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                    await ctx.send(embed=embed)
                elif roles not in target.roles:
                    await target.add_roles(roles)
                    embed = discord.Embed(description=f":white_check_mark: I have assigned **{Name}** to {target.mention}",
                                          timestamp=datetime.utcnow(),
                                          color=0x77B255)
                    embed.set_footer(text=f'Actioned by: {ctx.author} / {ctx.author.id}')
                    await ctx.send(embed=embed)

    @giveyou.command()
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

    @giveyou.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, name=None):
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
    
    @giveyou.command()
    async def list(self, ctx):
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        msg = 'List of all tags:\n'

        for i in db['giveyou']:
            msg = msg + '**' + i['name'] + '**\n'

        await ctx.send(msg)


def setup(bot):
    bot.add_cog(giverole(bot))
    print('giverole module loaded')
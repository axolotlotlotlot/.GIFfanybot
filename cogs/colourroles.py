import discord
import json
from discord.ext import commands

jsonPath = 'colourroles.json'
with open(jsonPath) as fopen:
    data = json.load(fopen)


def findroleid(roleName, guild):
    roles = guild.roles
    for i in roles:
        if i.name == roleName:
            return i.id
    return None


def saveInfo():
    with open(jsonPath, 'w') as outFile:
        json.dump(data, outFile, indent=4)

class ColourRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(alias='addcolourrole')
    @commands.has_role('Mods')
    async def colourmeadd(self, ctx, roleName):
        if roleName in data['Roles']:
            await ctx.send('This role already exists!')
            return

        roleID = findroleid(roleName, ctx.guild)
        if roleID == None:
            await ctx.send(
                "I couldn't find a role with the name **{0}**. Are you sure it exists?".format(roleName))

        data['Roles'][roleName] = [roleID, '', '', '', '']
        await ctx.send('Rank **{0}** has been added!'.format(roleName))

        saveInfo()

    @commands.command(alias='removecolourrole')
    @commands.has_role('Mods')
    async def colourmeremove(self, ctx, *roleNames):
        if not roleNames:
            await ctx.send('You need to type at least one role name!')
            return

        for i in roleNames:
            if i not in data['Roles']:
                await ctx.send('I could not find a role with the name **{0}**. Are you sure it exists?'.format(i))
                continue

            data['Roles'].pop(i)
            await ctx.send('The role **{0}** has been removed!'.format(i))

        saveInfo()

    @commands.command()
    @commands.has_role('Weirdness Experts')
    async def colourme(self, ctx, rankName):
        if rankName not in data['Roles']:
            await ctx.send("I couldn't find a role with that name.")
            return

        role = ctx.guild.get_role(data['Roles'][rankName][0])

        if role not in ctx.author.roles:
            await ctx.author.add_roles(role)

            if data['Roles'][rankName][1] == '':
                await ctx.send('{0}, I have assigned **{1}**'.format(ctx.author.mention, role.name))

            else:
                await ctx.send(data['Roles'][rankName][1].format(ctx.author.mention, role.name))

            if data['Roles'][rankName][2] != '':
                embed = discord.Embed(title='', description='')
                embed = embed.set_image(url=data['Roles'][rankName][2])
                await ctx.send(content=None, embed=embed)

        else:
            await ctx.author.remove_roles(role)

            if data['Roles'][rankName][3] == '':
                await ctx.send('{0}, I have removed **{1}**'.format(ctx.author.mention, role.name))

            else:
                await ctx.send(data['Roles'][rankName][3].format(ctx.author.mention, role.name))

            if data['Roles'][rankName][4] != '':
                embed = discord.Embed(title='', description='')
                embed = embed.set_image(url=data['Roles'][rankName][4])
                await ctx.send(content=None, embed=embed)


    @commands.command(alias='addyou')
    @commands.has_role('Weirdness Experts')
    async def colouryou(self, ctx, rankName):
        role: discord.Role
        member: discord.User = None
        if member == None:
            await ctx.channel.send("Please provide a member!")
            return

        if member == ctx.message.author:
            await ctx.send("You cannot use this on yourself!")
            return

        if rankName not in data['Roles']:
            await ctx.send("I couldn't find a role with that name.")
            return

        if role not in ctx.member.roles:
            await ctx.member.add_roles(role)

            if data['Roles'][rankName][1] == '':
                await ctx.send('{0}, I have assigned **{1}**'.format(ctx.member.mention, role.name))

            else:
                await ctx.send(data['Roles'][rankName][1].format(ctx.member.mention, role.name))

            if data['Roles'][rankName][2] != '':
                embed = discord.Embed(title='', description='')
                embed = embed.set_image(url=data['Roles'][rankName][2])
                await ctx.send(content=None, embed=embed)

        else:
            await ctx.member.remove_roles(role)

            if data['Roles'][rankName][3] == '':
                await ctx.send('{0}, I have removed **{1}**'.format(ctx.member.mention, role.name))

            else:
                await ctx.send(data['Roles'][rankName][3].format(ctx.member.mention, role.name))

            if data['Roles'][rankName][4] != '':
                embed = discord.Embed(title='', description='')
                embed = embed.set_image(url=data['Roles'][rankName][4])
                await ctx.send(content=None, embed=embed)


    @commands.command()
    @commands.has_role('Weirdness Experts')
    async def colourlist(self, ctx):
        msg = 'List of self-assignable colour roles for Weirdness Experts:\n'

        for i in data['Roles']:
            msg = msg + '**' + i + '**\n'

        await ctx.send(msg)




def setup(bot):
    bot.add_cog(ColourRoles(bot))

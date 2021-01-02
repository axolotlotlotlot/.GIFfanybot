import os

import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["userinfo"])
    async def whois(self, ctx, member: discord.Member = None):
        """Shows you the current information about a member. If member is not provided it will instead show your information. Use: <p>whois <member> Aliases:userinfo"""
        if member == None:  # if member is no mentioned
            member = ctx.message.author  # set member as the author
        roles = [role for role in member.roles]
        embed = discord.Embed(colour=discord.Colour.from_rgb(230, 230, 230), timestamp=ctx.message.created_at,
                              title=f"User Info - {member}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}")

        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Display Name:", value=member.display_name)

        embed.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

        embed.add_field(name="Roles:", value="".join([role.mention for role in roles[1:]]))
        embed.add_field(name="Highest Role:", value=member.top_role.mention)
        print(member.top_role.mention)
        await ctx.send(embed=embed)

    @commands.command(aliases=["whatsdat"])
    async def serverinfo(self, ctx):
        """Shows you the current information about the server. Aliases:whatsdat"""
        guild = ctx.guild
        embed = discord.Embed(title=f"Server Info", colour=discord.Colour.from_rgb(230, 230, 230))
        embed.set_author(name=f'{guild.name}', icon_url=f'{guild.icon_url}')
        embed.set_thumbnail(url=f'{guild.icon_url}')
        embed.add_field(name='Server Owner', value=f'{guild.owner.mention}', inline=False)
        embed.add_field(name='Members', value=f'{guild.member_count}', inline=False)
        embed.add_field(name="Channels:", value=len(guild.channels), inline=False)
        embed.add_field(name="Roles:", value=len(guild.roles), inline=False)
        embed.add_field(name='Boost Level', value=f'{guild.premium_tier}', inline=False)
        embed.add_field(name='Created At', value=f'{guild.created_at}', inline=False)
        embed.add_field(name='Region', value=f'{guild.region}', inline=False)
        embed.add_field(name='ID', value=f'{guild.id}', inline=True)

        await ctx.send(embed=embed)

    @commands.command(aliases=["pfp"])
    async def avatar(self, ctx, member: discord.Member = None):
        """Shows you your avatar, or members avatar if member is provided. Use: <p>avatar <member>"""
        if member == None:
            member = ctx.message.author
            filename = f"{member}.gif"
            await ctx.author.avatar_url.save(filename)
            file = discord.File(fp=filename)
            await ctx.send("Enjoy :>", file=file)
            filepath = './{0}'.format(filename)
            os.remove(filepath)
        else:
            filename = f"{member}.gif"
            await member.avatar_url.save(filename)
            file = discord.File(fp=filename)
            await ctx.send("Enjoy :>", file=file)
            filepath = './{0}'.format(filename)
            os.remove(filepath)

def setup(bot):
    bot.add_cog(General(bot))
    print('general module loaded')
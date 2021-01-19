import discord
import sqlite3
import datetime
from discord.ext import commands

class Limbo(commands.Cog):
    """Limbo module"""
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def limbo(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Put member to limbo. Use: <p>limbo <member> <reason>"""
        limborole = discord.utils.get(ctx.guild.roles, name="Limbo")
        db = sqlite3.connect('limbo.db')
        cursor = db.cursor()
        role_ids = ",".join([str(role.id) for role in member.roles[1:]])

        if member == ctx.message.author:
            await ctx.channel.send("You cannot limbo yourself!")
            return

        if member == None:
            await ctx.channel.send("Please provide a user!")
            return

        if limborole in member.roles:
            await ctx.send(f"{member} is already limboed")
            return

        sql = ("INSERT INTO limbo(guild_id, user_id, roles_ids) VALUES(?, ?, ?)")
        val = (ctx.guild.id, member.id, role_ids)

        await member.edit(roles=[])
        await member.add_roles(limborole, reason=reason)
        #await member.move_to(736680179253903491)
        embed = discord.Embed(title="Member was thrown to limbo", timestamp=datetime.datetime.utcnow(),
                              color=discord.Colour.from_rgb(21, 177, 239))
        embed.set_thumbnail(url=f'{member.avatar_url}')
        embed.add_field(name="\n\u200b",
                        value=member.mention + " was limboed for " + reason + " by " + ctx.message.author.mention,
                        inline=False)
        embed.set_footer(text=f'User ID: {member.id}')
        await ctx.send(embed=embed)

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unlimbo(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Releases member from limbo. Use: <p>unlimbo <member>"""
        limborole = discord.utils.get(ctx.guild.roles, name="Limbo")
        main = sqlite3.connect('limbo.db')
        cursor = main.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        if member == ctx.message.author:
            await ctx.channel.send("You cannot limbo yourself!")
            return

        if member == None:
            await ctx.channel.send("Please provide a user!")
            return

        if limborole not in member.roles:
            await ctx.send(f"{member.mention} is not in limbo")
            return

        if limborole in member.roles:

            role_ids = field(f"SELECT roles_ids FROM limbo WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
            roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

            if roles in member.roles:
                await ctx.send(f"Can't give {member.mention} roles he already has")
                return

            await member.edit(roles=roles)
            sql = (f"DELETE FROM limbo WHERE guild_id = {ctx.guild.id} AND user_id = {member.id}")
            await member.remove_roles(limborole, reason=reason)
            embed = discord.Embed(title="Member was thrown out from limbo", timestamp=datetime.datetime.utcnow(),
                                  color=discord.Colour.from_rgb(21, 177, 239))
            embed.set_thumbnail(url=f'{member.avatar_url}')
            embed.add_field(name="\n\u200b",
                            value=member.mention + " was unlimboed for " + reason + " by " + ctx.message.author.mention,
                            inline=False)
            embed.set_footer(text=f'User ID: {member.id}')
            await ctx.send(embed=embed)
            cursor.execute(sql)
        main.commit()
        cursor.close()
        main.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM logs WHERE guild_id = {message.guild.id}")
        result = cursor.fetchone()
        channel = self.bot.get_channel(736680179253903491)
        logchannel = self.bot.get_channel(id=int(result[0]))
        if message.channel == channel:
            embed = discord.Embed(title="Limbo log", timestamp=datetime.datetime.utcnow(), color=discord.Colour.from_rgb(76, 150, 255))
            embed.set_thumbnail(url=f'{message.author.avatar_url}')
            embed.add_field(name=f"{message.author}", value=f"{message.content}", inline=False)
            embed.set_footer(text=f'User ID: {message.author.id}')
            await logchannel.send(embed=embed)
        db.commit()
        cursor.close()
        db.close()



def setup(bot):
    bot.add_cog(Limbo(bot))
    print('limbo module loaded')

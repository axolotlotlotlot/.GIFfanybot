import discord
from discord.ext import commands

class Limbo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        channel = self.bot.get_channel(191635957538226176)
        if discord.utils.get(before.roles, name="Limbo"):
            if str(after.status) == "offline":
                channel.send(f"{after.name} has gone {after.status}.")



    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def limbo(self, ctx, member: discord.Member = None):
        guild = ctx.guild
        
        limborole = discord.utils.get(ctx.guild.roles, name="Limbo")

        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot limbo yourself! Please provide a correct user!")
            return



        await member.remove_roles(member.roles)
        await member.add_roles(limborole)
        await member.move_to(736680179253903491)
        await ctx.send(f"{member} has been limboed.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unlimbo(self, ctx, member: discord.Member = None):
        guild = ctx.guild
        limborole = discord.utils.get(ctx.guild.roles, name="Limbo")

        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot unlimbo yourself! Please provide a correct user!")
            return
        await member.remove_roles(limborole)
        await member.move_to(149167686159564800)
        await ctx.send(f"{member} has been unlimboed.")





def setup(bot):
    bot.add_cog(Limbo(bot))

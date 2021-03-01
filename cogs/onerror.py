import discord
from discord import Embed, Member, NotFound, Object
from discord.ext.commands import Greedy, Converter, BadArgument
from discord.ext import commands


class OnError(commands.Cog):
    """Moderation module"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = Embed(description=f":x: You don't have permissions to perform that action",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        if isinstance(error, commands.UserNotFound):
            embed = Embed(description=f":x: User not found",
                          color=0xDD2222)
            await ctx.send(embed=embed)

        if isinstance(error, commands.CommandOnCooldown):
            embed = Embed(
                description=":x: Command on cooldown, try again later.",
                color=0xDD2222)
            await ctx.send(embed=embed)












def setup(bot):
    bot.add_cog(OnError(bot))
    print('moderation module loaded')
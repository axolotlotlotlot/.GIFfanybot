import discord
from discord.ext import commands

class Moderation(commands.Cog):
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
    async def ban(self, ctx, member: discord.User = None, *, reason=None):
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot ban yourself! Please provide a correct user!")
            return
        if reason == None:
            reason = "No reason provided."
        message = f"You have been banned from {ctx.guild.name} for {reason}."
        await ctx.guild.ban(member, reason=reason)
        await ctx.channel.send(f"{member} is banned.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User = None, *, reason=None):
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot unban yourself! Please provide a correct user!")
            return
        if reason == None:
            reason = "No reason provided."
        message = f"You have been unbanned from {ctx.guild.name} for {reason}."
        await ctx.guild.unban(member, reason=reason)
        await ctx.channel.send(f"{member} is unbanned.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.User = None, *, reason=None):
        if member == None or member == ctx.message.author:
            await ctx.channel.send("You cannot kick yourself! Please provide a correct user!")
            return
        if reason == None:
            reason = "No reason provided."
        message = f"You have been kicked from {ctx.guild.name} for {reason}."
        await ctx.guild.kick(member, reason=reason)
        await ctx.channel.send(f"{member} is kicked.")

    @commands.command(aliases=["purge", "clear", "clean"])
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, amount=2):
        await ctx.channel.purge(limit=amount)




def setup(bot):
    bot.add_cog(Moderation(bot))
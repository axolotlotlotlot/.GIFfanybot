import discord
import chat_exporter
from discord.ext import commands


class ChatExporter(commands.Cog):
    """Chat exporter module."""
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        chat_exporter.init_exporter(self.bot) # to get the info if the user left the guild

    @commands.command(alias=['export', 'logchannel', 'log'])
    @commands.has_permissions(administrator=True)
    async def archive(self, ctx):
        """Exports and archives channel into an .html file. For large channels it can take several minutes. Use: <p>archive Aliases:export, logchannel"""
        await chat_exporter.export(ctx)

def setup(bot):
    bot.add_cog(ChatExporter(bot))
    print('chat exporter module loaded')
import discord
import chat_exporter
from discord.ext import commands


class ChatExporter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        chat_exporter.init_exporter(self.bot) # to get the info if the user left the guild

    @commands.command(alias='export')
    @commands.has_permissions(manage_messages=True)
    async def logchannel(self, ctx):
        await chat_exporter.export(ctx)

def setup(bot):
    bot.add_cog(ChatExporter(bot))
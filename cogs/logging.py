import discord
import chat_exporter
from discord.ext import commands





class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = self.bot.get_channel(785206949192400896)
        embed = discord.Embed(colour=discord.Colour.from_rgb(237, 42, 45))
        embed.set_author(name=f'{message.author}')
        embed.set_thumbnail(url=f'{message.author.avatar_url}')
        embed.add_field(name=f"Message sent by:",
                        value=f"{message.author.mention} was deleted in {message.channel.mention}", inline=False)
        embed.add_field(name="Deleted message:", value=f'{message.content}', inline=False)
        embed.set_footer(text=f"User ID: {message.author.id}/Message ID: {message.id}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        channel = self.bot.get_channel(785206949192400896)
        if channel:
            embed = discord.Embed(colour=discord.Colour.from_rgb(247, 205, 66))
            embed.set_author(name=f'{before.author}')
            embed.set_thumbnail(url=f'{before.author.avatar_url}')
            embed.add_field(name=f"Message sent by:",
                        value=f"{before.author.mention} was edited in {after.channel.mention}", inline=False)
            embed.add_field(name="Original message:", value=before.content)
            embed.add_field(name="Edited message:", value=after.content)
            embed.add_field(name="...", value=f"[Jump to message.]({after.jump_url})")
            embed.set_footer(text=f"User ID: {before.author.id}")
            await channel.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(Logging(bot))

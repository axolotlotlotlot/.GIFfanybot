import discord
import datetime
from discord.ext import commands

class Starboard(commands.Cog):
    """Starboard module"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, member):
        schannel = self.bot.get_channel(320878957425721344)

        if (reaction.emoji == '⭐') and (reaction.count >= 3):
            embed = discord.Embed(color=discord.Colour.from_rgb(247, 205, 66))
            embed.set_author(name=reaction.message.author.name, icon_url=reaction.message.author.avatar_url)
            embed.add_field(name="Message Content", value=reaction.message.content)
            embed.add_field(name="Original", value=f"[Jump to message.]({reaction.message.jump_url})")

            if len(reaction.message.attachments) > 0:
                embed.set_image(url=reaction.message.attachments[0].url)

            embed.set_footer(text=f" ⭐ {reaction.count} | # {reaction.message.channel.name}")
            embed.timestamp = datetime.datetime.utcnow()
            await schannel.send(embed=embed)



def setup(bot):
    bot.add_cog(Starboard(bot))
    print('starboard module loaded')
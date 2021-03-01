import discord
from discord.ext import commands

class ReactionRoles(commands.Cog):
    """reaction roles module"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        member = payload.member
        channelid = '191629998027833344'
        channel = self.bot.get_channel(191629998027833344)
        if payload.channel_id == 191629998027833344 and payload.message_id == 716270653145219094:
            if payload.emoji.name == "👍":
                gfcrole = discord.utils.get(payload.member.guild.roles, name='Gravity Falls Citizens')
                if gfcrole in member.roles:
                    print(f'{member} already is a member of this guild.')
                    return
                else:
                    await member.add_roles(gfcrole)
                    print(f'{member} was given GFC role.')

def setup(bot):
    bot.add_cog(ReactionRoles(bot))
    print('reaction roles module loaded')

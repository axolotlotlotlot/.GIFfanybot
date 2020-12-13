import discord
from discord.ext import commands





class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        channel = self.bot.get_channel(149167686159564800)
        if len(before.roles) < len(after.roles):
            newRole = next(role for role in after.roles if role not in before.roles)
            if newRole.name == "Gravity Falls Citizens":
                await channel.send(f"Welcome {after.mention} to {after.guild}! Enjoy your time here!")
                await channel.send("https://gravity-falls.is-serious.business/707be0.png")

    #@commands.Cog.listener()
    #async def on_raw_reaction_add(self, payload):
        #message_id = payload.message_id
        #member = payload.member
        #channel = self.bot.get_channel(604071095280336947)
        #if message_id == 716270653145219094:
            #if payload.emoji.name == '+1':
                #await channel.send(f"Welcome {member.mention} to r/GravityFalls! Enjoy your time here!")
                #await channel.send("https://gravity-falls.is-serious.business/707be0.png")


def setup(bot):
    bot.add_cog(Welcomer(bot))
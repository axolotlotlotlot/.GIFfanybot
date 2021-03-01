import discord
import sqlite3
from discord.ext import commands


def guildid(ctx):
    ctx.guild.id

class Welcomer(commands.Cog):
    """Welcomer module"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM welcomer WHERE guild_id = {before.guild.id}")
        result = cursor.fetchone()
        limborole = discord.utils.get(before.guild.roles, name="Limbo")
        rejoin = discord.utils.get(before.guild.roles, name="rejoin")
        if result is None:
            return

        if limborole in before.roles:
            return

        if rejoin in before.roles:
            return

        if len(before.roles) < len(after.roles):
            newRole = next(role for role in after.roles if role not in before.roles)
            if newRole.name == "Gravity Falls Citizens":
                cursor.execute(f"SELECT msg FROM welcomer WHERE guild_id = {before.guild.id}")
                result1 = cursor.fetchone()
                member = before.mention
                guild = before.guild
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(str(result1[0]).format(member=member, guild=guild))
                #name = after.display_name
                #if name == 'Bill Cipher':
                    #cursor.execute(f"SELECT msg2 FROM welcomer WHERE guild_id = {before.guild.id}")
                    #result2 = cursor.fetchone()
                    #member = before.mention
                    #guild = before.guild
                    #channel = self.bot.get_channel(id=int(result[0]))
                    #await channel.send(str(result2[0]).format(member=member, guild=guild))
        cursor.close()
        db.close()

    @commands.group(invoke_without_command=True)
    @commands.has_role('Mods')
    async def welcome(self, ctx):
        """Sets welcome channel and essage. Use:<p>welcome channel <channel> and <p>welcome text <message>"""
        await ctx.send('Available setup commands: \nwelcome channel <channel>\nwelcome text <message>')


    @welcome.command()
    async def channel(self, ctx, channel: discord.TextChannel):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM welcomer WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO welcomer(guild_id, channel_id) VALUES(?, ?)")
            val = (ctx.guild.id, channel.id)
            await ctx.send(f"Channel for welcome message has been set to {channel.mention}")
        elif result is not None:
            sql = ("UPDATE welcomer SET channel_id = ? WHERE guild_id = ?")
            val =  (channel.id, ctx.guild.id)
            await ctx.send(f"Channel for welcome message has been updated to {channel.mention}")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @welcome.command()
    async def message(self, ctx, *, text):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM welcomer WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO welcomer(guild_id, msg) VALUES(?, ?)")
            val = (ctx.guild.id, text)
            await ctx.send(f"Welcome message has been set to '{text}'")
        elif result is not None:
            sql = ("UPDATE welcomer SET msg = ? WHERE guild_id = ?")
            val = (text, ctx.guild.id)
            await ctx.send(f"Welcome message has been updated to '{text}'")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()














































# @commands.Cog.listener()
  #  async def on_raw_reaction_add(self, payload):
   #     message_id = payload.message_id
    #    member = payload.member
     #   channel = self.bot.get_channel(604071095280336947)
      #  if payload.channel_id == 787637594791739413 and payload.message_id == 787637665855307808:
       #     if payload.emoji.name == "👍":
        #        role = discord.utils.get(payload.member.guild.roles, name='Gravity Falls Citizens')
         #       if role in member.roles:
          #          print(f'{member} already is a member of this guild.')
           #         return
            #    else:
             #       await channel.send(f"Welcome {member.mention} to r/GravityFalls! Enjoy your time here!")
              #      await channel.send("https://gravity-falls.is-serious.business/707be0.png")
               #     await member.add_roles(role)
                #    print(f'{member} was given GFC role.')




def setup(bot):
    bot.add_cog(Welcomer(bot))
    print('welcomer module loaded')

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
    async def message(self, ctx, *, text=None):
        db = sqlite3.connect('journal3.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM welcomer WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if text is None:
            return
        if result is None:
            sql = ("INSERT INTO welcomer(guild_id, msg) VALUES(?, ?)")
            val = (ctx.guild.id, text)
            embed = discord.Embed(title=f":white_check_mark: Welcome message has been set to:\n'{text}'",
                                  timestamp=datetime.datetime.utcnow(),
                                  color=0x77B255)
            await ctx.send(embed=embed)
        elif result is not None:
            sql = ("UPDATE welcomer SET msg = ? WHERE guild_id = ?")
            val = (text, ctx.guild.id)
            embed = discord.Embed(title=f":white_check_mark: Welcome message has been set to:\n'{text}'",
                                  timestamp=datetime.datetime.utcnow(),
                                  color=0x77B255)
            await ctx.send(embed=embed)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        dbs = sqlite3.connect('journal3.db')
        cursor = dbs.cursor()
        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        prefix = field('SELECT prefix FROM prefixes WHERE guildid = {0}'.format(message.guild.id))
        cursor.close
        dbs.close
        create = f'{prefix}welcome message'
        if message.content == create:
            channel = message.channel
            if message.author.guild_permissions.administrator:
                embed = discord.Embed(
                    description="Welcome message creation started. Please provide welcome message contents. I will save your next message as the welcome message contents, or type `abort` to abort the process.",
                    color=message.author.top_role.colour)
                startembed = await channel.send(embed=embed)

                def check(m):
                    return m.channel == channel and m.author == message.author

                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=check)

                except asyncio.TimeoutError:
                        embed = discord.Embed(
                            description=f":x: Uh oh, {message.author.mention}! You took longer than 1 minute to respond, welcome message creation cancelled.",
                            color=0xDD2222)
                        await channel.send(embed=embed)
                        await startembed.delete()
                        await message.delete()
                        return

                abort = ['abort', 'Abort', 'ABort', 'ABOrt', 'ABORt', 'ABORT', 'aBORT', 'abORT', 'aboRT', 'aborT']

                if msg.content in abort:
                    embed = discord.Embed(
                        description=":x: Tag creation process aborted",
                        color=0xDD2222)
                    await channel.send(embed=embed)
                    await startembed.delete()
                    await msg.delete()
                    await message.delete()
                    return

                elif msg.content not in abort:
                    db = sqlite3.connect('journal3.db')
                    cursor = db.cursor()
                    cursor.execute(f"SELECT channel_id FROM welcomer WHERE guild_id = {message.guild.id}")
                    result = cursor.fetchone()
                    if result is None:
                        sql = ("INSERT INTO welcomer(guild_id, msg) VALUES(?, ?)")
                        val = (message.guild.id, msg.content)
                        embed = discord.Embed(title=f":white_check_mark: Welcome message has been set to:\n'{msg.content}'",
                                              timestamp=datetime.datetime.utcnow(),
                                              color=0x77B255)
                        await channel.send(embed=embed)
                        await message.delete()
                        await startembed.delete()
                        await msg.delete()
                    elif result is not None:
                        sql = ("UPDATE welcomer SET msg = ? WHERE guild_id = ?")
                        val = (msg.content, message.guild.id)
                        embed = discord.Embed(title=f":white_check_mark: Welcome message has been set to:\n'{msg.content}'",
                                              timestamp=datetime.datetime.utcnow(),
                                              color=0x77B255)
                        await channel.send(embed=embed)
                        await message.delete()
                        await startembed.delete()
                        await msg.delete()
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

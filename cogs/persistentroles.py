import dataset
import discord
import sqlite3
from discord.ext import commands

class persistentroles(commands.Cog):
    """Makes roles persistent when members leave, and will give them back when they rejoin."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['banned']
        users = table.find(guildid=member.guild.id, userid=member.id)
        for user in users:
            if member.id == user['userid']:
                return
        GFC = discord.utils.get(member.guild.roles, name="Gravity Falls Citizens")
        muted = discord.utils.get(member.guild.roles, name="Muted")

        if (GFC in member.roles) or (muted in member.roles):
            proles = ",".join([str(role.id) for role in member.roles[1:]])
            db = dataset.connect('sqlite:///journal3.db')
            db.begin()
            table = db['persistentroles']
            table.insert(dict(guildid=member.guild.id, userid=member.id, roles=proles))
            db.commit()


    @commands.Cog.listener()
    async def on_member_join(self, member):
        main = sqlite3.connect('journal3.db')
        cursor = main.cursor()

        def field(command, *values):
            cursor.execute(command, tuple(values))

            for row in cursor.fetchall():
                return row[0]

        db = dataset.connect('sqlite:///journal3.db')
        db.begin()
        table = db['persistentroles']
        users = table.find(guildid=member.guild.id, userid=member.id)
        for user in users:
            if member.id == user['userid']:
                rejoin = discord.utils.get(member.guild.roles, name="rejoin")
                await member.add_roles(rejoin)
                role_ids = field("SELECT roles FROM persistentroles WHERE userid = {0} AND guildid = {1}".format(member.id, member.guild.id))
                proles = [member.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]
                await member.edit(roles=proles)
                await member.remove_roles(rejoin)
                sql = ("DELETE FROM persistentroles WHERE guildid = {0} AND userid = {1}".format(member.guild.id, member.id))
                cursor.execute(sql)
                main.commit()
        cursor.close()
        main.close()

def setup(bot):
    bot.add_cog(persistentroles(bot))
    print('persistent roles module loaded')

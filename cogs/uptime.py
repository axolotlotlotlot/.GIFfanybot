#https://github.com/khk4912/BGM-Discord-Bot/blob/master/commands/uptime.py
import logging
import discord
from discord.ext import commands
import datetime


class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_start_time = datetime.datetime.utcnow()

    def create_logger(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.DEBUG)
        if logger.hasHandlers():
            logger.handlers.clear()

        formatter = logging.Formatter(
            "[%(asctime)s][%(name)s][%(levelname)s] %(message)s "
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        filehandler = logging.FileHandler(
            "Bot_Logs/{}.txt".format(self.__class__.__name__), "w"
        )
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
        logger.addHandler(stream_handler)
        logger.info("{} Loaded.".format(self.__class__.__name__))
        return logger

    @classmethod
    def main_logger(cls):
        logger = logging.getLogger("discord")
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s][%(name)s][%(levelname)s] %(message)s "
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        filehandler = logging.FileHandler(
            "Bot_Logs/{}.txt".format(cls.__name__), "w"
        )
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
        logger.addHandler(stream_handler)
        return logger

    @commands.command()
    async def uptime(self, ctx):
        uptime = datetime.datetime.utcnow() - self.bot_start_time

        day = uptime.days
        day = str(day)

        uptime = str(uptime)
        uptime = uptime.split(":")

        hours = uptime[0]

        hours = hours.replace(" days,", "Days")
        hours = hours.replace(" day,", "Day")

        minitues = uptime[1]

        seconds = uptime[2]
        seconds = seconds.split(".")
        seconds = seconds[0]

        embed = discord.Embed(
            title="🕐 Uptime",
            description="The bot has been online for %s hours %s minutes %s seconds."
                        % (hours, minitues, seconds),
            color=0x237CCD,
            timestamp=self.bot_start_time)
        embed.set_footer(text="Bot start time")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Uptime(bot))
#from carberra https://github.com/Carberra/updated-discord.py-tutorial
from random import choice, randint
from typing import Optional

import dataset
import discord
from aiohttp import request
from discord import Member, Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown


class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="hello", aliases=["hi"])
	async def say_hello(self, ctx):
		await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya', 'I am sure you will never abandon me, new boyfriend', 'https://i.imgur.com/R9MrDgO.gif'))} {ctx.author.mention}!")

	@command(name="dice", aliases=["roll"])
	@cooldown(1, 60, BucketType.user)
	async def roll_dice(self, ctx, die_string: str):
		dice, value = (int(term) for term in die_string.split("d"))

		if dice <= 25:
			rolls = [randint(1, value) for i in range(dice)]

			await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

		else:
			await ctx.send("I can't roll that many dice. Please try a lower number.")

	@command(name="slap", aliases=["hit"])
	async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "for no reason"):
		db = dataset.connect('sqlite:///journal3.db')
		db.begin()
		table = db['userfilter']
		users = table.all(guild=ctx.guild.id, user=ctx.author.id)
		for user in users:
			if user['user'] == ctx.author.id:
				await ctx.send("You're not allowed to use this command")
				return

		MT = discord.utils.get(ctx.guild.roles, name="Mystery Twins")
		if MT in ctx.author.roles:
			await ctx.send(f"{ctx.author.display_name} slapped {member.mention} {reason}!")
		else:
			await ctx.send("You can use this command only if you're Mystery Twins rank")

	@slap_member.error
	async def slap_member_error(self, ctx, exc):
		if isinstance(exc, BadArgument):
			await ctx.send("I can't find that member.")

	@command(name="fact")
	@cooldown(3, 60, BucketType.guild)
	async def animal_fact(self, ctx, animal: str):
		db = dataset.connect('sqlite:///journal3.db')
		db.begin()
		table = db['userfilter']
		users = table.all(guild=ctx.guild.id, user=ctx.author.id)
		for user in users:
			if user['user'] == ctx.author.id:
				await ctx.send("You're not allowed to use this command")
				return

		MT = discord.utils.get(ctx.guild.roles, name="Gnomes")
		if MT in ctx.author.roles:
			if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala"):
				fact_url = f"https://some-random-api.ml/facts/{animal}"
				image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

				async with request("GET", image_url, headers={}) as response:
					if response.status == 200:
						data = await response.json()
						image_link = data["link"]

					else:
						image_link = None

				async with request("GET", fact_url, headers={}) as response:
					if response.status == 200:
						data = await response.json()

						embed = Embed(title=f"{animal.title()} fact",
									  description=data["fact"],
									  colour=ctx.author.colour)
						if image_link is not None:
							embed.set_image(url=image_link)
						await ctx.send(embed=embed)

					else:
						await ctx.send(f"API returned a {response.status} status.")

			else:
				await ctx.send("No facts are available for that animal.")
		else:
			await ctx.send("You can use this command only if you're Gnome rank")

def setup(bot):
	bot.add_cog(Fun(bot))
	print('fun module loaded')

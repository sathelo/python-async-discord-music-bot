import discord
from discord.ext import commands
from discord.flags import Intents

import music_configuration
from settings import TOKEN


cogs = [music_configuration]
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(bot)


# Events
@bot.command()
async def bots(ctx):
    await ctx.send('На месте! ✅')


# Commands
@bot.command()
async def patch(ctx):
    await ctx.send('patch 1.1.3')


bot.run(TOKEN)

import discord
import music_configuration
from discord.ext import commands
from dotenv import load_dotenv
from os import environ


load_dotenv()
cogs = [music_configuration]
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(bot)


# Events
@bot.command()
async def bots(ctx):
    await ctx.send('На месте! ✅')


# Get token
bot.run(environ['TOKEN'])

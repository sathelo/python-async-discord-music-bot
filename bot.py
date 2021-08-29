import discord
import music_configuration
import about_configuration
from discord.ext import commands
from dotenv import load_dotenv
from os import environ


load_dotenv()
cogs = [music_configuration, about_configuration]

activity = discord.Activity(
    name='Music by Sathelo | !help',
    type=discord.ActivityType.listening
)
bot = commands.Bot(
    command_prefix='!',
    activity=activity
)

for i in range(len(cogs)):
    cogs[i].setup(bot)


# Get token
bot.run(environ['TOKEN'])

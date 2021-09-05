import discord
import music_configuration
import about_configuration
from discord.ext.commands.context import Context
from discord.ext import commands
from dotenv import load_dotenv
from os import environ, stat
from discord_components import DiscordComponents


load_dotenv()
cogs = [music_configuration, about_configuration]

status = discord.Status.online
activity = discord.Activity(
    name='Music by Sathelo | !help',
    type=discord.ActivityType.listening
)
bot = commands.Bot(
    command_prefix='!',
    activity=activity,
    status=status
)


@bot.event
async def on_ready():
    DiscordComponents(bot)


@bot.event
async def on_command_error(ctx: Context, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Такой команды не существует, прости 😓")


for i in range(len(cogs)):
    cogs[i].setup(bot)


# Get token
bot.run(environ['TOKEN'])

import discord
from discord import channel
from discord.colour import Color
from discord.ext import commands
from discord.ext.commands import Context


class AboutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def about(self, ctx: Context):
        """ Информация о боте

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        text = ("""```По всем вопросам\ntelegram: @normalfaggot```""")
        emb = discord.Embed(title='О нас', color=discord.Colour.green())
        emb.add_field(
            name='Создатель: Sathelo\nОтдельное спасибо Gudlayv', value=text)
        emb.set_thumbnail(url='https://i.redd.it/du43v8zp2y961.jpg')
        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(AboutCog(bot))

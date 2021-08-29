import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord_components import Button, ButtonStyle


class AboutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def about(self, ctx: Context):
        """ Информация о боте

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        description = ("""```Если хотите новый патч```""")
        one_button = Button(
            style=ButtonStyle.URL,
            label="telegram",
            url="https://t.me/normalfaggot"
        )
        two_button = Button(
            style=ButtonStyle.URL,
            label="github",
            url="https://github.com/sathelo"
        )
        three_button = Button(
            style=ButtonStyle.URL,
            label="vk",
            url="https://vk.com/sashenkoalex"
        )

        emb = discord.Embed(title='О нас', color=discord.Colour.red())
        emb.add_field(
            name='Создатель: Sathelo\nОтдельное спасибо Gudlayv\n\nПо всем вопросам 👇', value=description)
        emb.set_thumbnail(url='https://i.redd.it/du43v8zp2y961.jpg')
        await ctx.send(
            embed=emb,
            components=[
                [one_button,
                 two_button,
                 three_button]
            ]
        )


def setup(bot):
    bot.add_cog(AboutCog(bot))

import discord
import youtube_dl
from discord import VoiceClient
from discord.ext import commands
from discord.ext.commands import Context
from youtube_dl.utils import DownloadError


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def __check_access(self, ctx: Context) -> bool:
        """ Проверка доступа к командам

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.

        Returns:
            bool: True - если пользователь в голосов чате
        """
        name = await self.__get_username(ctx)
        if ctx.author.voice:
            return True

        await ctx.send(f"{name} ты не в голосовом канале ⁉")
        return False

    async def __get_username(self, ctx: Context) -> str:
        """ Получить имя пользователя

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.

        Returns:
            str: Для обычных пользователей это просто их имя пользователя, но если у них есть псевдоним, специфичный для гильдии, он возвращается.
        """
        return ctx.author.display_name

    @commands.command()
    async def join(self, ctx: Context):
        """ Присоединение в голосовой в чат

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        name = await self.__get_username(ctx)
        voice_client: VoiceClient = ctx.voice_client
        if not await self.__check_access(ctx):
            return
        if isinstance(voice_client, VoiceClient) and voice_client.is_connected():
            await ctx.send(f"{name} я уже подключен, в глазки долбишься ⁉")
            return
        channel = ctx.author.voice.channel
        await channel.connect()

    @commands.command()
    async def disconnect(self, ctx: Context):
        """ Отключение из голосового в чат

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        name = await self.__get_username(ctx)
        voice_client: VoiceClient = ctx.voice_client
        if not await self.__check_access(ctx):
            return
        if voice_client is None:
            await ctx.send(f"{name} я уже отключен, в глазки долбишься ⁉")
            return
        await voice_client.disconnect()

    @commands.command()
    async def play(self, ctx: Context, url: str):
        """ Запуск youtube клипа по ссылке

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
            url (str): Ссылка на youtube клип
        """
        if not await self.__check_access(ctx):
            return
        name = await self.__get_username(ctx)
        voice_client: VoiceClient = ctx.voice_client
        if voice_client is None:
            await ctx.send(f'{name} будь добр напиши !join ⁉')
            return
        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format': "bestaudio"}
        vc = ctx.voice_client
        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                vc.play(source)
        except DownloadError:
            await ctx.send(f'{name} ты не передал сыллку ⁉')

    @commands.command()
    async def pause(self, ctx: Context):
        """ Приостановить youtube клип

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        name = await self.__get_username(ctx)
        voice_client: VoiceClient = ctx.voice_client
        if not await self.__check_access(ctx):
            return
        if voice_client is None:
            await ctx.send(f'{name} будь добр напиши !join ⁉')
            return
        if not voice_client.is_playing():
            await ctx.send(f"{name} я сейчас не играю музыку ⁉")
            return
        voice_client.pause()
        await ctx.send(f"{name} поставил паузу ⏸")

    @commands.command()
    async def resume(self, ctx: Context):
        """ Возобновить youtube клип

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        name = await self.__get_username(ctx)
        voice_client: VoiceClient = ctx.voice_client
        if not await self.__check_access(ctx):
            return
        if voice_client is None:
            await ctx.send(f'{name} будь добр напиши !join ⁉')
            return
        if not voice_client.is_paused():
            await ctx.send(f"{name} ты сначала поставь на паузу, а потом меня вызывай ⁉")
            return
        voice_client.resume()
        await ctx.send(f"{name} продолжил песню ⏯")

    @commands.command()
    async def skip(self, ctx: Context):
        """ Пропустить youtube клип

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        name = await self.__get_username(ctx)
        voice_client: VoiceClient = ctx.voice_client
        if not await self.__check_access(ctx):
            return
        if voice_client is None:
            await ctx.send(f'{name} будь добр напиши !join ⁉')
            return
        if isinstance(voice_client, VoiceClient) and not voice_client.is_playing():
            await ctx.send(f'{name} песен больше не осталось, может скипнуть тебя ⁉')
            return
        voice_client.stop()
        await ctx.send(f"{name} скипнул песню 💨")


def setup(bot):
    bot.add_cog(MusicCog(bot))

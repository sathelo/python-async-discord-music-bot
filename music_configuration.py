import discord
from discord.ext.commands.core import command
import youtube_dl
from discord import VoiceClient
from discord.ext import commands
from discord.ext.commands import Context
from youtube_dl.utils import DownloadError
from asyncio import sleep
import time


TIMEOUT_DISCONNECT_SECOND = 60


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_list = []
        self.context = None
        self.is_loop = False
        self.is_play = False
        self.timeout_disconnect: int = None

    def __has_next(self, voice_client: VoiceClient) -> bool:
        """ Проверка переключения музыки

        Args:
            voice_client (VoiceClient): голосовой клиент

        Returns:
            bool: True - переключить музыку
        """
        # Если музыка играет
        if voice_client.is_playing():
            return False

        # Если пустой список песен
        if not len(self.song_list):
            return False

        # Если песня на пазуе
        if voice_client.is_paused():
            return False

        # Если песня включается
        if self.is_play:
            return False

        return True

    async def __disconnect(self, ctx: Context):
        """ Отключение из голосового чата

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        self.is_loop = False
        self.song_list = []
        voice_client: VoiceClient = ctx.voice_client

        if voice_client is None:
            return

        await voice_client.disconnect()

    async def __play(self, ctx: Context, url: str):
        """ Запуск youtube клипа

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
            url (str): Ссылка на youtube клип
        """
        while self.is_play:
            await sleep(0.5)
        self.is_play = True
        voice_client: VoiceClient = ctx.voice_client
        voice_client.stop()
        try:
            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            YDL_OPTIONS = {'format': "bestaudio"}
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                voice_client.play(source)
                await ctx.send('Сейчас играет - ' + info.get('title'))
        except:
            raise
        finally:
            self.is_play = False

    async def __loop(self, ctx: Context):
        """ Цикл событий

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        # Если передали контекс обновить его иначе оставить старый
        if not ctx is None:
            self.context = ctx

        # Если контекста нет, то выходим
        if self.context is None:
            return

        # Если нет voice_client, то выходим
        voice_client: VoiceClient = self.context.voice_client
        if not isinstance(voice_client, VoiceClient):
            return

        voice_client: VoiceClient = self.context.voice_client

        voice_client.loop.create_task(self.__playlist(self.context))
        voice_client.loop.create_task(self.__iamalon(self.context))

        # Добавляем проверку в цикл событий еще раз
        await sleep(1)
        voice_client.loop.create_task(self.__loop(self.context))

    async def __playlist(self, ctx: Context = None):
        """ Обработчик плейлиста

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        voice_client: VoiceClient = self.context.voice_client

        self.is_loop = True

        # Сделать проверку и запуск музыки из очереди
        song_list_len = len(self.song_list)
        if self.__has_next(voice_client):
            url = self.song_list.pop(0)
            voice_client.loop.create_task(self.__play(self.context, url))
            await ctx.send(f'Песен осталось/Песен в очереди: {song_list_len}')

    async def __iamalon(self, ctx):
        """ Обработчик одиночества

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
        """
        users_ids = list(ctx.voice_client.channel.voice_states.keys())
        if (len(users_ids) > 1):
            self.timeout_disconnect = None
            return

        if self.timeout_disconnect is None:
            self.timeout_disconnect = time.time()

        timeout = time.time() - self.timeout_disconnect
        if not timeout > TIMEOUT_DISCONNECT_SECOND:
            return

        self.timeout_disconnect = None
        ctx.voice_client.loop.create_task(self.__disconnect(self.context))

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
        """ Присоединение в голосовой чат

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
        if not self.is_loop:
            await self.__loop(ctx)

    @commands.command()
    async def play(self, ctx: Context, url: str):
        """ Запуск youtube клипа по ссылке

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
            url (str): Ссылка на youtube клип
        """
        name = await self.__get_username(ctx)
        voice_client: VoiceClient = ctx.voice_client
        if not await self.__check_access(ctx):
            return
        if voice_client is None:
            await ctx.send(f'{name} будь добр напиши !join ⁉')
            return
        voice_client.stop()
        try:
            voice_client.loop.create_task(self.__play(ctx, url))
        except DownloadError:
            await ctx.send(f'{name} ты не передал сыллку ⁉')

    @commands.command()
    async def add_song(self, ctx: Context, url: str):
        """ Добавление youtube клипа в очередь

        Args:
            ctx (Context): Представляет контекст, в котором вызывается команда.
            url (str): Ссылка на youtube клип
        """
        name = await self.__get_username(ctx)
        voice_client: VoiceClient = ctx.voice_client
        if not await self.__check_access(ctx):
            return
        if voice_client is None:
            await ctx.send(f'{name} будь добр напиши !join ⁉')
            return
        self.song_list.append(url)
        if voice_client.is_playing():
            await ctx.send(f'Песен осталось/Песен в очереди: {len(self.song_list)}')

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

from typing import ContextManager
import discord
from discord.ext import commands

from discord import VoiceClient
import youtube_dl


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event check exist
    async def check_exist(self, ctx):
        name = str(ctx.author).split('#')[0]
        if not ctx.author.voice:
            await ctx.send(f"{name} ты не в голосовом канале ⁉")
            return False
        return True

    # Command join
    @commands.command()
    async def join(self, ctx):
        name = str(ctx.author).split('#')[0]
        voice_client: VoiceClient = ctx.voice_client
        if not await self.check_exist(ctx):
            return
        if isinstance(voice_client, VoiceClient) and voice_client.is_connected():
            await ctx.send(f"{name} я уже подключен, в глазки долбишься ⁉")
            return
        channel = ctx.author.voice.channel
        await channel.connect()

    # Command disconnect
    @commands.command()
    async def disconnect(self, ctx):
        name = str(ctx.author).split('#')[0]
        voice_client: VoiceClient = ctx.voice_client
        if not await self.check_exist(ctx):
            return
        if voice_client is None:
            await ctx.send(f"{name} я уже отключен, в глазки долбишься ⁉")
            return
        await ctx.voice_client.disconnect()

    # Command play
    @commands.command()
    async def play(self, ctx, url):
        if not await self.check_exist(ctx):
            return
        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format': "bestaudio"}
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source)

    # Command pause
    @commands.command()
    async def pause(self, ctx):
        name = str(ctx.author).split('#')[0]
        voice_client: VoiceClient = ctx.voice_client
        if not await self.check_exist(ctx):
            return
        if not voice_client.is_playing():
            await ctx.send(f"{name} я сейчас не играю музыку ⁉")
            return
        ctx.voice_client.pause()
        await ctx.send(f"{name} поставил паузу ⏸")

    # Command resume
    @commands.command()
    async def resume(self, ctx):
        name = str(ctx.author).split('#')[0]
        voice_client: VoiceClient = ctx.voice_client
        if not await self.check_exist(ctx):
            return
        if not voice_client.is_paused():
            await ctx.send(f"{name} ты сначала поставь на паузу, а потом меня вызывай ⁉")
            return
        ctx.voice_client.resume()
        await ctx.send(f"{name} продолжил песню ⏯")

    # Command skip
    @commands.command()
    async def skip(self, ctx):
        name = str(ctx.author).split('#')[0]
        voice_client: VoiceClient = ctx.voice_client
        if not await self.check_exist(ctx):
            return
        if isinstance(voice_client, VoiceClient) and not voice_client.is_playing():
            await ctx.send(f'{name} песен больше не осталось, может скипнуть тебя ⁉')
            return
        ctx.voice_client.stop()
        await ctx.send(f"{name} скипнул песню 💨")


def setup(bot):
    bot.add_cog(music_cog(bot))

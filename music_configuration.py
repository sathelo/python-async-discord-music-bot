import discord
from discord.ext import commands

import youtube_dl


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command join
    @commands.command()
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("Ты не в голосовом канале ⁉")
        else:
            channel = ctx.author.voice.channel
            await channel.connect()

    # Command disconnect
    @commands.command()
    async def disconnect(self, ctx):
        await ctx.voice_client.disconnect()

    # Command play
    @commands.command()
    async def play(self, ctx, url):
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
        try:
            ctx.voice_client.pause()
            await ctx.send(f"{name} поставил паузу ⏸")
        except:
            await ctx.send(f"{name} я сейчас не играю музыку ⁉")

    # Command resume
    @commands.command()
    async def resume(self, ctx):
        name = str(ctx.author).split('#')[0]
        try:
            ctx.voice_client.resume()
            await ctx.send(f"{name} продолжил песню ⏯")
        except:
            await ctx.send(f"{name} я сейчас не играю музыку ⁉")


def setup(bot):
    bot.add_cog(music_cog(bot))

import discord
from discord.ext import commands
import youtube_dl

# Set up bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Set up YouTube downloader
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
        return
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Bot has left the channel")
    else:
        await ctx.send("Bot is not in a voice channel")

@bot.command(name='play', help='To play song')
async def play(ctx, url):
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

    await ctx.send(f'Now playing: {player.title}')

@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    await ctx.send("Paused the song")
    ctx.voice_client.pause()

@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    await ctx.send("Resumed the song")
    ctx.voice_client.resume()

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    await ctx.send("Stopped the song")
    ctx.voice_client.stop()

bot.run('MTI3MTg2NDA1MDI4Mzk3NDc5MQ.G7tDGr.iMqNsmQm3rl9iVTuzzo8rZivRH-7FRcH3JFG8o')
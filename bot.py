import discord
import random
import asyncio

# FIXME:
import spotipy

# FIXME: youtube player?
import re
import youtube_dl
import os

from discord.utils import get
from discord.ext import commands, tasks
from collections import deque
from credentials import BOT_TOKEN

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


# song queue
song_queue = deque()

# create bot
bot = commands.Bot(command_prefix=".")

# song queue
song_queue = deque()


# listen for events: actions that happen in server
# bot is done preparing data received by Discord after successful login
@bot.event
async def on_ready():
    print("Bot is ready for use...")
    # start status loop
    change_status.start()


# bot status options
status_list = [
    "Boba Assimilator",
    "Sarcasm Generator",
    "Resting Dock",
    "Chill Bot Vibes",
    "Binary Rock",
    "IU Best Hits",
    "Android X Mingle",
]
# randomly pick status
@tasks.loop(seconds=180)
async def change_status():
    await bot.change_presence(activity=discord.Game(random.choice(status_list)))


# TODO:
@bot.command()
async def autoplay(ctx):
    ctx.send("Autoplay enabled for queued songs.")
    check_next_song_ready.start(ctx)


@tasks.loop(seconds=10)
async def check_next_song_ready(ctx):
    global song_queue
    # bot must be in voice channel. Get voice client
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and not voice.is_playing() and song_queue:
        await play(ctx, url=None)
    else:
        return


# handle command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please pass in required arguments for this command!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to run this command!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("That command does not exist.")
    print(error)


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! Your latency is {round(bot.latency * 1000)} ms.")


# alias allows users to call command via different names
@bot.command(aliases=["8ball", "8 ball", "8_ball", "ball", "ask", "question"])
async def eight_ball(ctx, *question):
    question_words_set = {
        "who",
        "what",
        "when",
        "where",
        "why",
        "how",
        "whom",
        "is",
        "are",
        "am",
    }
    eight_ball_responses = [
        "As I see it, yes.",
        " Ask again later.",
        " Better not tell you now.",
        " Cannot predict now.",
        " Concentrate and ask again.",
        " Don’t count on it.",
        "It is certain.",
        " It is decidedly so.",
        " Most likely.",
        " My reply is no.",
        " My sources say no.",
        "Outlook not so good.",
        "Outlook good.",
        "Reply hazy, try again.",
        "Signs point to yes.",
        " Very doubtful.",
        "Without a doubt.",
        " Yes.",
        " Yes – definitely.",
        "You may rely on it.",
    ]
    print(question)
    if question == ():
        await ctx.send("You didn't ask me a question...")
    elif question[-1].endswith("?") or question[0].lower() in question_words_set:
        await ctx.send(random.choice(eight_ball_responses))

    else:
        await ctx.send("I would like you to phrase that as a question.")


# clear message history
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, number_messages=1):
    number_messages = min(number_messages, 25)
    purge_message = (
        "Yeeting last message."
        if number_messages == 1
        else f"Obliviate last {number_messages} messages."
    )
    await ctx.send(purge_message)
    await asyncio.sleep(4)
    await ctx.channel.purge(limit=number_messages + 2)


# music functionalities
@bot.command()
async def join(ctx):
    member_in_vc = ctx.message.author.voice
    if not member_in_vc:
        await ctx.send("User must be in a voice channel before using this command.")
        return
    channel = ctx.message.author.voice.channel

    voice = ctx.message.guild.voice_client
    # move bot from existing vc
    if voice and voice.is_connected():
        await voice.move_to(channel)
    # bot not in any vc
    else:
        voice = await channel.connect()


@bot.command(pass_context=True)
async def leave(ctx):
    voice = ctx.message.guild.voice_client
    if voice:
        await voice.disconnect()
        extension_cleanup(".webm")
    else:
        await ctx.send("I am not currently in any voice channels.")


# TODO:
@bot.command(name="play", help="This command plays songs")
async def play(ctx, url=None):
    global song_queue
    server = ctx.message.guild
    # bot must be in voice channel. Get voice client
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send(
            "You must summon the bot into voice channel using `.join` first!"
        )
        return
    voice_channel = server.voice_client

    # cannot call play while voice is actively playing
    if voice.is_playing():
        await ctx.send(
            "There is already a song playing. You may:\n  - add a song to queue using `.add`\n  - play song immediately by using `.pause` then `.play <url>`    "
        )
        return

    # play url: if voice is paused or stopped
    if url:
        song_queue.appendleft(url)

        async with ctx.typing():
            player = await YTDLSource.from_url(song_queue[0], loop=bot.loop)
            voice_channel.play(
                player, after=lambda e: print("Player error: %s" % e) if e else None
            )

        await ctx.send("**Now Playing:**\n{}".format(player.title))
        del song_queue[0]
        #
    else:
        # no url provided, play next song from queue
        if song_queue:
            # TODO: refactor
            async with ctx.typing():
                player = await YTDLSource.from_url(song_queue[0], loop=bot.loop)
                voice_channel.play(
                    player, after=lambda e: print("Player error: %s" % e) if e else None
                )

            await ctx.send("**Now Playing:**\n{}".format(player.title))
            del song_queue[0]
            #
        else:
            await ctx.send(
                "You must specify a url after `.play` when using command with empty queue."
            )


@bot.command(
    pass_context=True,
    aliases=["Pause", "Stop", "stop"],
)
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.pause()


@bot.command(
    pass_context=True, brief="Resumes the music that is playing", aliases=["Resume"]
)
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.resume()


@bot.command(
    pass_context=True, brief="Skips the music that is playing", aliases=["Skip"]
)
async def skip(ctx):
    await ctx.send("Ended current song. Call `.play` to play next song.")
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


@bot.command(aliases=["add", "push"])
async def add_song(ctx, url: str):
    pattern = re.compile(r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$")
    url_match = pattern.search(url)
    if url_match:
        song_queue.append(url)
        await ctx.send("Added song to back of queue")
        await display_queue(ctx)
    else:
        await ctx.send(
            "Unable to find url. Enqueue song using format `.add <youtube_url>`"
        )


@bot.command(aliases=["removefront", "removenext"])
async def remove_front(ctx):
    try:
        song_queue.popleft()
        await ctx.send("Removed song from front of queue.")
        await display_queue(ctx)
    except IndexError:
        await ctx.send("Nothing to remove from empty queue.")


@bot.command(aliases=["remove", "removeback", "removelast"])
async def remove_back(ctx):
    try:
        song_queue.pop()
        await ctx.send("Removed song from back of queue.")
        await display_queue(ctx)
    except IndexError:
        await ctx.send("Queue is empty - Nothing to remove.")


@bot.command(aliases=["q", "list", "songlist"])
async def show_queue(ctx):
    await display_queue(ctx)


# FIXME: volume function
@bot.command()
async def set_volume(ctx, volume):
    pass


async def display_song(ctx, song_name):
    song_name = song_name.rsplit("-", 1)
    await ctx.send(f"Playing: {song_name[0]}")
    print(f"Playing: {song_name[0]}")


async def display_queue(ctx):
    if song_queue:
        queue_display = ""
        for idx, song in enumerate(song_queue, start=1):
            queue_display += f"\n**{idx}.**   {song}"
        await ctx.send(queue_display)
    else:
        await ctx.send("Song queue is empty!")


def extension_cleanup(extension):
    # Store path of directory containing file
    file_directory = os.path.dirname(__file__)
    for file in os.listdir(file_directory):
        if file.endswith(extension):
            os.unlink(file_directory + "/" + file)


# def dl_youtube_song(url):
#     """ Download from youtube url as mp3 """
#     ydl_opts = {
#         "format": "bestaudio/best",
#         "postprocessors": [
#             {
#                 "key": "FFmpegExtractAudio",
#                 "preferredcodec": "mp3",
#                 "preferredquality": "192",
#             }
#         ],
#     }

#     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#         print("Downloading audio now\n")
#         ydl.download([url])
#         print("finish")


# run bot with token (link code to app so code can manipulate app)
bot.run(BOT_TOKEN)

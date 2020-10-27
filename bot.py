import discord
import random
import asyncio

# FIXME:
import spotipy

# FIXME: youtube player?
import youtube_dl
import os

from discord.utils import get
from discord.ext import commands
from collections import deque
from credentials import BOT_TOKEN

# dict of players in form {server_id : player}
players = dict()

# song queue
song_queue = deque()

# create bot
bot = commands.Bot(command_prefix=".")

# listen for events: actions that happen in server
# bot is done preparing data received by Discord after successful login
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("sarcastic comments"))
    print("Bot is ready for use...")


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
    channel = ctx.message.author.voice.channel
    if not channel:
        ctx.send("Connect to a voice channel before using this command.")
        return
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
    else:
        await ctx.send("I am not currently in any voice channels.")


# TODO:
@bot.command(pass_context=True, aliases=["p", "pla"])
async def play(ctx, url: str):
    # bot must be in voice channel. Get voice client
    voice = get(bot.voice_clients, guild=ctx.guild)

    # return if play is called while a song is playing
    if voice.is_playing():
        await ctx.send("There is already a song playing.")
        return

    # if play is called from empty queue, initialize queue with song
    if not song_queue:
        song_queue.append(url)

    await play_next_song(ctx, song_queue.pop(), voice)


# TODO:
async def play_next_song(ctx, url, voice):
    # clear any old mp3
    remove_mp3()
    await ctx.send("Song request received")

    dl_youtube_song(url)
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "current_song.mp3")

    voice.play(
        discord.FFmpegPCMAudio("current_song.mp3"),
        # AFTER SONG COMPLETION
        after=lambda e: print("finished current song"),
    )

    # add transformer to change volume
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.04

    await display_song(ctx, name)


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
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


@bot.command(aliases=["add", "push"])
async def add_song(ctx, url: str):
    song_queue.append(url)
    await ctx.send("Added song to back of queue")
    await display_queue(ctx)


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
            queue_display += f"\n{idx}. {song}"
        await ctx.send(queue_display)
    else:
        await ctx.send("Song queue is empty!")


def dl_youtube_song(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])
        print("finish")


def remove_mp3():
    song_there = os.path.isfile("song.mp3")
    if song_there:
        os.remove("song.mp3")
        print("Removed old song file")


# run bot with token (link code to app so code can manipulate app)
bot.run(BOT_TOKEN)

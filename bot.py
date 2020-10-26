import discord
import random
import asyncio

from discord.ext import commands
from credentials import bot_token

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


# @bot.event
# async def on_member_join(member):
#     print(f'{member} has joined the server!')

# @bot.event
# async def on_member_remove(member):
#     print(f'{member} has left the server.')


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! Your latency is {round(bot.latency * 1000)} ms.")


# alias allows users to call command via different names
@bot.command(aliases=["8ball", "8 ball", "8_ball", "ball", "ask", "question"])
async def eight_ball(ctx, *question):
    question_words_set = {"who", "what", "when", "where", "why", "how", "whom"}
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
        await ctx.send(
            f"Your question:{question} " + random.choice(eight_ball_responses)
        )
    else:
        await ctx.send("I would like you to phrase that as a question.")


# clear message history
@bot.command()
async def purge(ctx, number_messages=1):
    purge_message = (
        "Yeeting last message."
        if number_messages == 1
        else f"Obliviate last {number_messages} messages."
    )
    await ctx.send(purge_message)
    await asyncio.sleep(4)
    await ctx.channel.purge(limit=number_messages + 2)


# @bot.command()
# async def shutdown(ctx):
#     await ctx.bot.logout()


# run bot with token (link code to app so code can manipulate app)
bot.run(bot_token)

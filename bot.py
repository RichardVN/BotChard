import discord
import random

from discord.ext import commands
from credentials import bot_token

# create bot
bot = commands.Bot(command_prefix=".")

# listen for events: actions that happen in server
# bot is done preparing data received by Discord after successful login
@bot.event
async def on_ready():
    print("Bot is ready for use...")


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
    if question == None:
        await ctx.send("You didn't ask me a question...")
    elif question[-1].endswith("?") or question[0].lower() in question_words_set:
        await ctx.send(
            f"Your question:{question} " + random.choice(eight_ball_responses)
        )
    else:
        await ctx.send("I would like you to phrase that as a question.")


# @bot.command()
# async def shutdown(ctx):
#     await ctx.bot.logout()


# run bot with token (link code to app so code can manipulate app)
bot.run(bot_token)

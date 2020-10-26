import discord
from discord.ext import commands
from credentials import bot_token

# create client
client = commands.Bot(command_prefix=".")


@client.event
async def on_ready():
    print("Bot is ready!")


# run client with token (link code to app so code can manipulate app)
client.run(bot_token)

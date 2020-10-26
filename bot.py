import discord
from discord.ext import commands

# create client
client = commands.Bot(command_prefix=".")

@client.event
async def on_ready():
    print('Bot is ready!')

# run client with token (link code to app so code can manipulate app)
client.run("NzcwMTMwNjQ3NjUzNDE2OTkw.X5ZGDg.-5_YIpxoZPgHRGggK5QmFTxymTE")

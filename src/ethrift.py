import json
import discord
from discord.ext import commands

with open('settings.json', 'r') as f:
    config = json.load(f)
    token = config["discord"]["token"]  

bot = commands.Bot(command_prefix='!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

bot.run(token)

import json
import discord
from discord.ext import commands

queries_list = []


class Query:
    def __init__(self, query, min_price, max_price):
        self.query = query
        self.min_price = min_price
        self.max_price = max_price
        self.items = []

    def formatted_query(self):
        return f"{self.query} | Min. Price: {self.min_price}$ | Max. Price: {self.max_price}$"

    def list_queries(self):
        result = ''
        for i, query in enumerate(queries_list):
            result += f"\n{i} | {query.formatted_query()}"
        return result


with open("settings.json", 'r') as f:
    config = json.load(f)
    token = config["discord"]["token"]

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command()
async def kill(ctx):
    await ctx.send("Goodbye!")
    await bot.logout()


@bot.command(aliases=["commands", "help"])
async def cmd(ctx):
    result = """
    ```
I am a simple bot to warn you about new items in eBay searches

Commands:
!help, !cmd or !commands -> Show this list of commands
!ping -> Checks if bot is online
    
!add <\"query keywords\"> <min. price> <max. price>
!del <indexes separated by spaces>
!queries -> Lists all currently active queries

!kill -> Shuts down the bot

made by @tiagosvf
```"""
    await ctx.send(result)


@bot.command(aliases=["searches", "list", "lst"])
async def queries(ctx):
    result = Query.list_queries(queries)
    if result:
        await ctx.send(f"```{result}```")
    else:
        await ctx.send("```You have not added any queries. \nAdd one using !add <\"query keywords\"> <min_price> <max_price>```")


@bot.command()
async def add(ctx, query, min_price, max_price):
    _query = Query(query, min_price, max_price)
    queries_list.append(_query)
    await ctx.send(f"Query \"{query}\" with minimum price of {min_price}$ and maximum price of {max_price}$ added")


@bot.command(aliases=["del", "rm", "rem", "remove"])
async def delete(ctx, *indexes):
    indexes = list(indexes)
    result = ''
    for index in sorted(indexes, reverse=True):
        try:
            result += f"\n{queries_list.pop(int(index)).formatted_query()}"
        except IndexError:
            indexes.remove(index)
    await ctx.send(f"```Removed {len(indexes)} queries: \n{result}```")


bot.run(token)

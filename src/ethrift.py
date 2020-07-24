import json
import discord
import asyncio
from discord.ext import commands

search_list = []


class Search:
    def __init__(self, query, min_price, max_price):
        self.query = query
        self.min_price = min_price
        self.max_price = max_price
        self.items = []

    def formatted_search(self):
        return f"{self.query} | Min. Price: {self.min_price}$ | Max. Price: {self.max_price}$"

    @staticmethod
    def list_searches():
        result = ''
        for i, search in enumerate(search_list):
            result += f"\n{i} | {search.formatted_search()}"
        return result

    @staticmethod
    async def save_searches():
        data = {}
        data['searches'] = []
        for search in search_list:
            data["searches"].append(
                {'query': search.query, 'min_price': search.min_price, 'max_price': search.max_price})
            await asyncio.sleep(0.01)
        with open('searches.txt', 'w') as outfile:
            json.dump(data, outfile, indent=4)

    @staticmethod
    def read_searches():
        try:
            with open('searches.txt') as json_file:
                data = json.load(json_file)
                for q in data['searches']:
                    search = Search(q['query'], q['min_price'], q['max_price'])
                    search_list.append(search)
        except FileNotFoundError:
            pass
        except KeyError:
            pass


with open("settings.json", 'r') as f:
    config = json.load(f)
    token = config["discord"]["token"]

Search.read_searches()

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
    embed = discord.Embed(title="\u200b\nI am a simple bot that warns you about new items in eBay searches",
                          description="\u200b\u200b", color=0xc200a8)
    embed.set_author(name="made by @tiagosvf", url="https://github.com/tiagosvf",
                     icon_url="https://avatars0.githubusercontent.com/u/25352856?s=460&u=f5b0c682e7634580340e2fea35bce3764686e02e&v=4")
    embed.add_field(name="Commands", value="!help, !cmd or !commands\n!ping\n\n!add <\"keywords\"> <min. price> <max. price>\n!del <indexes separated by spaces>\n!searches, !list or !lst\n\n!kill", inline=True)
    embed.add_field(
        name="\u200b", value="Shows this list of commands\nChecks if bot is online\n\n\n\nLists all currently active searches\n\nShuts down the bot", inline=True)
    await ctx.send(embed=embed)


@bot.command(aliases=["queries", "list", "lst"])
async def searches(ctx):
    result = Search.list_searches()
    if result:
        await ctx.send(f"```{result}```")
    else:
        await ctx.send("```You have not added any searches. \nAdd one using !add <\"query keywords\"> <min_price> <max_price>```")


@bot.command()
async def add(ctx, query, min_price, max_price):
    search = Search(query, min_price, max_price)
    search_list.append(search)
    await Search.save_searches()
    await ctx.send(f"Search \"{query}\" with minimum price of {min_price}$ and maximum price of {max_price}$ added")


@bot.command(aliases=["del", "rm", "rem", "remove"])
async def delete(ctx, *indexes):
    indexes = list(indexes)
    result = ''
    for index in sorted(indexes, reverse=True):
        try:
            result += f"\n{search_list.pop(int(index)).formatted_search()}"
        except IndexError:
            indexes.remove(index)
    await Search.save_searches()
    await ctx.send(f"```Removed {len(indexes)} searches: \n{result}```")


bot.run(token)

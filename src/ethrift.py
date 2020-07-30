import json
import discord
import asyncio
import ast
import math
from decimal import Decimal
from discord.ext import commands, tasks
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError

search_list = []
max_daily_ebay_calls = 5000


class Item:
    def __init__(self, id, title, price, url, location, condition,
                 thumbnail=None, start_time=None):
        self.id = id
        self.title = title
        self.price = price
        self.url = url
        self.location = location
        self.condition = condition
        self.thumbnail = thumbnail
        self.start_time = start_time

    def __eq__(self, other):
        return self.url == other.url

    async def display(self, channel_id):
        channel = bot.get_channel(channel_id)
        Decimal(f"{self.price}").quantize(Decimal("0.00"))
        embed = discord.Embed(
            title=f"{self.title}", url=f"{self.url}", description="", color=0xfaa61a)
        embed.set_thumbnail(url=f"{self.thumbnail}")
        embed.add_field(name="Price", value=f"{self.price}$", inline=True)
        embed.add_field(name="Location",
                        value=f"`{self.location}`", inline=True)
        embed.add_field(name="Condition",
                        value=f"`{self.condition}`", inline=True)
        await channel.send(embed=embed)

    @staticmethod
    def item_from_data(i):
        try:
            item = Item(id=i['itemId'],
                        title=i['title'],
                        price=i['sellingStatus']['convertedCurrentPrice']['value'],
                        url=i['viewItemURL'],
                        location=i['location'],
                        condition=i['condition']['conditionDisplayName'],
                        start_time=i['listingInfo']['startTime'])

            item.thumbnail = i['galleryURL']
        except KeyError:
            pass
        return item

    @staticmethod
    async def items_from_response(search, response, initializing):
        try:
            data = ast.literal_eval(str(response.dict()))
            newest_start_time = None
            for i in data['searchResult']['item']:
                item = Item.item_from_data(i)
                if not newest_start_time:
                    newest_start_time = item.start_time
                    newest_start_time = newest_start_time[:17] + str(
                        int(newest_start_time[17:19])+1) + newest_start_time[19:]
                    search.newest_start_time = newest_start_time
                if not initializing:
                    await item.display(search.channel_id)
                await asyncio.sleep(0.01)
        except KeyError:
            pass


class Search:
    def __init__(self, query, min_price, max_price, channel_id):
        self.query = query
        self.min_price = min_price
        self.max_price = max_price
        self.newest_start_time = None
        self.channel_id = channel_id

    async def add_to_list(self):
        search_list.append(self)
        await update_get_items_interval()
        await self.get_items(True)

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
                {'query': search.query, 'min_price': search.min_price,
                 'max_price': search.max_price,
                 'channel_id': search.channel_id})
            await asyncio.sleep(0.01)
        with open('searches.txt', 'w') as outfile:
            json.dump(data, outfile, indent=4)

    @staticmethod
    async def read_searches():
        try:
            with open('searches.txt') as json_file:
                data = json.load(json_file)
                for q in data['searches']:
                    search = Search(q['query'], q['min_price'], q['max_price'],
                                    q['channel_id'])
                    await search.add_to_list()
        except FileNotFoundError:
            pass
        except KeyError:
            pass
        get_items.start()

    async def get_items(self, initializing):
        try:
            api = Finding(config_file='ebay.yaml')

            api_request = {'keywords': f'{self.query}',
                           'itemFilter': [
                               {'name': 'Condition',
                                'value': ['New', '1500', '1750', '2000', '2500', '3000', '4000', '5000', '6000']},
                               {'name': 'LocatedIn',
                                'value': ['PT', 'ES', 'DE', 'CH', 'AT', 'BE', 'BG', 'CZ', 'CY', 'HR', 'DK', 'SI', 'EE', 'FI', 'FR', 'GR', 'HU', 'IE', 'IT', 'LT', 'LU', 'NL', 'PL', 'SE', 'GB']},
                               {'name': 'MinPrice', 'value': f'{self.min_price}',
                                'paramName': 'Currency', 'paramValue': 'USD'},
                               {'name': 'MaxPrice', 'value': f'{self.max_price}',
                                'paramName': 'Currency', 'paramValue': 'USD'},
                               {'name': 'ListingType',
                                'value': ['AuctionWithBIN', 'FixedPrice', 'StoreInventory', 'Classified']},
                               {'name': 'StartTimeFrom',
                                'value': f'{self.newest_start_time}'}
                           ],
                           'sortOrder': 'StartTimeNewest'}

            response = api.execute('findItemsAdvanced', api_request)

            await Item.items_from_response(self, response, initializing)
        except ConnectionError:
            pass

    @ staticmethod
    async def get_items_list():
        for search in search_list:
            await search.get_items(False)
            await asyncio.sleep(0.01)


with open("settings.json", 'r') as f:
    config = json.load(f)
    token = config["discord"]["token"]
    max_daily_ebay_calls = int(config["ebay"]["max_daily_api_calls"])

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')


@ bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@ bot.command()
async def kill(ctx):
    await ctx.send("Goodbye!")
    await bot.logout()


@ bot.command(aliases=["commands", "help"])
async def cmd(ctx):
    embed = discord.Embed(title="\u200b\nI am a simple bot that warns you about new items in eBay searches",
                          description="\u200b\u200b", color=0xc200a8)
    embed.set_author(name="ethrift by @tiagosvf", url="https://github.com/tiagosvf",
                     icon_url="https://avatars0.githubusercontent.com/u/25352856?s=460&u=f5b0c682e7634580340e2fea35bce3764686e02e&v=4")
    embed.add_field(name="Commands", value="!help, !cmd or !commands\n!ping\n\n!add <\"keywords\"> <min. price> <max. price>\n!del <indexes separated by spaces>\n!searches, !list or !lst\n\n!kill", inline=True)
    embed.add_field(
        name="\u200b", value="Shows this list of commands\nChecks if bot is online\n\n\n\nLists all currently active searches\n\nShuts down the bot", inline=True)
    await ctx.send(embed=embed)


@bot.command(aliases=["queries", "list", "lst"])
async def searches(ctx):
    result = Search.list_searches()
    if result:
        await ctx.send(f"```{result}\n\nFetching items every {get_items.minutes} minutes and {get_items.seconds} seconds```")
    else:
        await ctx.send("```You have not added any searches. \nAdd one using !add <\"query keywords\"> <min_price> <max_price>```")


@bot.command()
async def add(ctx, query, min_price, max_price):
    search = Search(query, min_price, max_price, ctx.channel.id)
    await search.add_to_list()
    await Search.save_searches()
    await ctx.send(f"Search \"{query}\" with minimum price of {min_price}$ and maximum price of {max_price}$ added")
    await search.get_items(True)


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
    await update_get_items_interval()
    await ctx.send(f"```Removed {len(indexes)} searches: \n{result}```")


@bot.command()
async def get(ctx):  # debugging TODO: delete
    await Search.get_items_list()


@bot.event
async def on_connect():
    await Search.read_searches()


@tasks.loop(seconds=18)
async def get_items():
    await Search.get_items_list()


async def update_get_items_interval():
    seconds = math.ceil((86400/max_daily_ebay_calls)*len(search_list))
    minutes = seconds//60
    seconds = seconds-(minutes*60)
    get_items.change_interval(minutes=minutes, seconds=seconds)

bot.run(token)

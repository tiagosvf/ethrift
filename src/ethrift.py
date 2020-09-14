import json
import discord
import asyncio
import ast
import math
import utils
from decimal import Decimal
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError

MAX_CHARACTERS = 1900

search_list = []
max_daily_ebay_calls = 5000
active_time = [datetime(1900, 1, 1, 0, 0, 0), datetime(1900, 1, 1, 0, 0, 0)]


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
        self.start_time_f = utils.str_to_datetime_ebay(self.start_time)

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
        return item if item else None

    @staticmethod
    async def items_from_response(search, response):
        try:
            data = ast.literal_eval(str(response.dict()))
            newest_start_time = utils.str_to_datetime_ebay(
                search.newest_start_time)
            aux_nst = newest_start_time

            for i in data['searchResult']['item']:
                item = Item.item_from_data(i)

                if item.start_time_f > aux_nst:
                    aux_nst = item.start_time_f
                    aux_nst = aux_nst + timedelta(seconds=3)
                elif item.start_time_f < newest_start_time:
                    break

                await item.display(search.channel_id)
                await asyncio.sleep(0.01)

            search.newest_start_time = utils.datetime_to_str_ebay(aux_nst)
        except KeyError:
            pass


class Search:
    def __init__(self, query, min_price, max_price, channel_id):
        self.query = query
        self.min_price = min_price
        self.max_price = max_price
        self.newest_start_time = None
        self.channel_id = channel_id
        self.newest_start_time = utils.datetime_to_str_ebay(datetime.utcnow())

    def add_to_list(self):
        search_list.append(self)
        update_get_items_interval()

    def formatted_search(self, widths):
        return f"{self.query: <{widths[1]}}  {self.min_price+'$' : >{widths[2]}}  {self.max_price+'$' : >{widths[3]}}"

    @staticmethod
    def get_table_column_width(list):
        widths = [len("Index"), len("Keywords"), len(
            "Max. Price"), len("Min. Price")]
        for i, search in enumerate(list):
            if utils.number_length(i) > widths[0]:
                widths[0] = utils.number_length(i)
            if len(search.query) > widths[1]:
                widths[1] = len(search.query)
            if len(search.min_price)+1 > widths[2]:
                widths[2] = len(search.min_price)+1
            if len(search.max_price)+1 > widths[3]:
                widths[3] = len(search.max_price)+1

        return widths

    @staticmethod
    def get_searches_table(list, page=1):
        widths = Search.get_table_column_width(list)
        result = f'{"Index": <{widths[0]}}  {"Keywords": <{widths[1]}}  {"Min. Price": <{widths[2]}}  {"Max. Price": <{widths[3]}}'
        result += '\n'.ljust(sum(widths)+7, '-')

        header_len = pagination_count = len(result)
        page_aux = 1

        for i, search in enumerate(list):
            aux_result = f"\n{i: <{widths[0]}}  {search.formatted_search(widths)}"
            pagination_count += len(aux_result)
            if pagination_count > MAX_CHARACTERS:
                page_aux += 1
                pagination_count = header_len
            if len(result) + len(aux_result) < MAX_CHARACTERS and page_aux == page:
                result += aux_result

        result += f"\n\n< {page} / {page_aux} >"

        return result

    @staticmethod
    def list_searches(page=1):
        return Search.get_searches_table(search_list, page)

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
    def read_searches():
        try:
            with open('searches.txt') as json_file:
                data = json.load(json_file)
                for q in data['searches']:
                    search = Search(q['query'], q['min_price'], q['max_price'],
                                    q['channel_id'])
                    search.add_to_list()
        except FileNotFoundError:
            pass
        except KeyError:
            pass
        get_items.start()

    async def get_items(self):
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

            await Item.items_from_response(self, response)
        except ConnectionError:
            pass

    @staticmethod
    async def get_items_list():
        for search in search_list:
            await search.get_items()
            await asyncio.sleep(0.02)


with open("settings.json", 'r') as f:
    config = json.load(f)
    token = config["discord"]["token"]
    max_daily_ebay_calls = int(config["ebay"]["max_daily_api_calls"])


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
    embed.set_author(name="ethrift by @tiagosvf", url="https://github.com/tiagosvf",
                     icon_url="https://avatars0.githubusercontent.com/u/25352856?s=460&u=f5b0c682e7634580340e2fea35bce3764686e02e&v=4")
    embed.add_field(name="Commands", value="`!help`, `!cmd` or `!commands` › Show this message"
                                           "\n`!ping` › Check if bot is online"
                                           "\n"
                                           "\n`!add <\"keywords\"> <min. price> <max. price>` › Add search"
                                           "\n`!del <indexes separated by spaces>` › Remove searches"
                                           "\n`!searches`, `!list` or `!lst` `[page]` › List all currently active searches"
                                           "\n"
                                           "\n`!active` › Check the bot's active hours"
                                           "\n`!active from <hh:mm> to <hh:mm>` › Set the bot's active hours"
                                           "\n"
                                           "\n`!kill` › Shut down the bot", inline=True)
    await ctx.send(embed=embed)


# TODO: add pagination when content exceeds 2000 characters
@bot.command(aliases=["queries", "list", "lst"])
async def searches(ctx, page=1):
    result = Search.list_searches(page)
    if result:
        await ctx.send(f"```{result}\n\nFetching items every {utils.get_items_interval_str(get_items)}```")
    else:
        await ctx.send("```You have not added any searches. \nAdd one using !add <\"query keywords\"> <min_price> <max_price>```")


@bot.command()
async def add(ctx, query, min_price, max_price):
    if hasattr(bot.get_channel(ctx.channel.id), 'recipient'):
        await ctx.send("```Not possible to use bot from this direct messages yet. \nInvite me to a channel and add searches from there please.```")
        return

    search = Search(query, min_price, max_price, ctx.channel.id)
    search.add_to_list()
    await Search.save_searches()
    await ctx.send(f"Search \"{query}\" with minimum price of {min_price}$ and maximum price of {max_price}$ added")


@bot.command(aliases=["del", "rm", "rem", "remove"])
async def delete(ctx, *indexes):
    indexes = list(indexes)
    removed_searches = []
    for index in sorted(indexes, reverse=True):
        try:
            removed_searches.append(search_list.pop(int(index)))
        except IndexError:
            indexes.remove(index)
    result = Search.get_searches_table(removed_searches)
    await Search.save_searches()
    update_get_items_interval()
    await ctx.send(f"```Removed {len(indexes)} searches: \n\n{result}```")


@bot.command()
async def get(ctx):  # debugging TODO: delete
    await Search.get_items_list()


@bot.command()
async def active(ctx,  *args):
    args = list(args)
    global active_time
    if len(args) == 0:
        await ctx.send(f"```Active and looking for new items {utils.get_active_time_str(active_time)}```")
    else:
        try:
            if len(args) < 4:
                await ctx.send("```Missing arguments.\nUse command as follows: !active from 08:30 to 23:00```")
                return
            if args[0].lower() != 'from' or args[2].lower() != 'to':
                await ctx.send("```Invalid or missing arguments.\nUse command as follows: !active from 08:30 to 23:00```")
                return
            active_time = [datetime.strptime(args[1], "%H:%M"),
                           datetime.strptime(args[3], "%H:%M")]

            update_get_items_interval()
            await ctx.send(f"```Active time changed\nI will be looking for items {utils.get_active_time_str(active_time)} every {utils.get_items_interval_str(get_items)}```")
        except ValueError:
            await ctx.send("```Invalid time format\nTime should be in HH:MM format like 08:30```")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.CommandError):
        print(f"Error: {error}")
        await ctx.send("```An error occured.\nUse !help to make sure you used the command correctly.```")


@tasks.loop(seconds=18)  # TODO: Handle errors
async def get_items():
    if(utils.is_time_between(active_time[0].time(), active_time[1].time())):
        await Search.get_items_list()


def update_get_items_interval():
    seconds = utils.seconds_between_times(active_time[0], active_time[1])
    seconds = 86400 if seconds == 0 else seconds
    seconds = math.ceil((seconds/max_daily_ebay_calls)*len(search_list))
    minutes, seconds = divmod(seconds, 60)
    get_items.change_interval(minutes=minutes, seconds=seconds)


Search.read_searches()


bot.run(token)

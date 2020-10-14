# External modules
import json
import ast
import threading
import time
import yaml
import discord
import asyncio

from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
from decimal import Decimal
from datetime import datetime, timedelta

# Internal modules
import ethrift
import utils
import data
import bot


MAX_CHARACTERS = 1900
MAX_THREADS = 20
MAX_QUEUE = 100

settings = {"domain": None, "appid": None, "version": None, "max_calls": 5000}

queue = []
threads = []
search_list = []


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

    def display(self, channel_id):
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
        utils.async_from_sync(ethrift.get_event_loop(),
                              channel.send, embed=embed)

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
    def items_from_response(search, response):
        try:
            data_r = ast.literal_eval(str(response.dict()))
            newest_start_time = utils.str_to_datetime_ebay(
                search.newest_start_time)
            aux_nst = newest_start_time

            for i in data_r['searchResult']['item']:
                item = Item.item_from_data(i)

                if item.start_time_f > aux_nst:
                    aux_nst = item.start_time_f
                    aux_nst = aux_nst + timedelta(seconds=3)
                elif item.start_time_f < newest_start_time:
                    break

                item.display(search.channel_id)

            search.newest_start_time = utils.datetime_to_str_ebay(aux_nst)
        except KeyError:
            pass


class Search:
    def __init__(self, query, min_price, max_price, channel_id,
                 newest_start_time=utils.datetime_to_str_ebay(datetime.utcnow())):
        self.query = query
        self.min_price = min_price
        self.max_price = max_price
        self.newest_start_time = None
        self.channel_id = channel_id
        self.newest_start_time = newest_start_time

    def add_to_list(self):
        search_list.append(self)
        bot.update_get_items_interval()

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
        data_s = {}
        data_s['searches'] = []
        for search in search_list:
            data_s["searches"].append(
                {'query': search.query, 'min_price': search.min_price,
                 'max_price': search.max_price,
                 'channel_id': f"{search.channel_id}"})
            await asyncio.sleep(0.01)
        data.save(data_s)

    @staticmethod
    def read_searches():
        try:
            json_s = data.read()
            data_s = json.loads(json_s)
            for q in data_s['searches']:
                search = Search(q['query'], q['min_price'], q['max_price'],
                                int(q['channel_id']))
                search.add_to_list()
        except KeyError:
            pass
        bot.start_get_items()

        for i in range(MAX_THREADS):
            get_items_thread = threading.Thread(
                target=Search.get_items, name=f"Getter{i}", daemon=True)
            threads.append(get_items_thread)
            get_items_thread.start()

    @staticmethod
    def get_items():
        while True:
            try:
                self = queue.pop(0)
                try:
                    api = Finding(domain=settings.get("domain"),
                                  appid=settings.get("appid"),
                                  version=settings.get("version"),
                                  config_file=None)

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

                    Item.items_from_response(self, response)
                except ConnectionError:
                    pass
            except IndexError:
                time.sleep(0.01)
                continue
            except Exception as e:  # idc just stop breaking
                print(f"Exception in get_items: {e}")

    @staticmethod
    async def get_items_list():
        for search in search_list:
            if len(queue) < MAX_QUEUE:
                queue.append(search)


def get_max_calls():
    return settings.get('max_calls')


def get_search_list():
    return search_list


def read_settings():
    with open(utils.get_file_path("settings.yaml")) as file:
        _settings = yaml.safe_load(file)

        global settings
        settings["max_calls"] = _settings["ebay"]["max_daily_calls"]
        settings["domain"] = _settings["ebay"]["domain"]
        settings["appid"] = _settings["ebay"]["appid"]
        settings["version"] = _settings["ebay"]["version"]


def main():
    read_settings()
    Search.read_searches()

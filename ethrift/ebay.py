# External modules
import json
import ast
import urllib.parse as urlparse
import threading
import time
import yaml
import discord
import asyncio

from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
from urllib.parse import parse_qs
from decimal import Decimal
from datetime import datetime, timedelta

# Internal modules
import utils
import data
import mapping
import bot


MAX_CHARACTERS = 1024
MAX_THREADS = 20
MAX_QUEUE = 100

settings = {"domain": None, "appid": None, "version": None, "max_calls": 5000}

queue = []
threads = []
search_list = []


class Filters(dict):
    def __init__(self, *arg, **kw):
        super(Filters, self).__init__(*arg, **kw)

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def get(self, key):
        return self.__dict__.get(key)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def copy(self):
        aux = Filters()
        aux.__dict__ = self.__dict__.copy()
        return aux

    def iterate_locatedin(self):
        self['LocatedIn'] = self.get('LocatedIn')[25:]
        if not self.get('LocatedIn'):
            return False

    def slice_locatedin(self):
        if self.get('LocatedIn'):
            self['LocatedIn'] = self.get('LocatedIn')[:25]

    def get_as_list(self):
        filter_list = []
        for filter in self:
            filter_list.append(
                {'name': filter, 'value': self[filter]})
        return filter_list

    def get_for_request(self):
        result = self.copy()

        # ebay only allows up to 25 countries in the located in filter
        if not self.iterate_locatedin():
            self = None

        result.slice_locatedin()
        result_list = result.get_as_list()

        return result_list, self

    @staticmethod
    def filter_response_items(search, item_response):
        """Verify if item matches search filters

        Some filters like items accepting best offers can't be set specifically
        in the request and need to be checked per item in the response
        """

        parsed = urlparse.urlparse(search.url)
        query = urlparse.parse_qs(parsed.query)

        if query.get('LH_BO') \
           and item_response['listingInfo']['bestOfferEnabled'] == "false":
            return False

        return True

    @staticmethod
    def map_located_in_filter(global_id, query):
        prefloc = query.get('LH_PrefLoc')

        if not prefloc:
            return None

        return mapping.map_global_id_located_in(global_id, prefloc)

    @staticmethod
    def get_from_query(query, ebay_site):
        filters = Filters()

        if query.get('_udlo'):
            filters['MinPrice'] = query.get('_udlo')[0]
        if query.get('_udhi'):
            filters['MaxPrice'] = query.get('_udhi')[0]

        if query.get('LH_ItemCondition'):
            condition = mapping.map_condition_ids(query)
            filters['Condition'] = condition

        listing_type = mapping.map_ebay_query_to_listing_type(query)
        if listing_type:
            filters['ListingType'] = listing_type

        located_in = Filters.map_located_in_filter(ebay_site, query)
        if located_in:
            filters['LocatedIn'] = located_in

        return filters


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
        channel = bot.get_bot().get_channel(channel_id)
        Decimal(f"{self.price}").quantize(Decimal("0.00"))
        embed = discord.Embed(
            title=f"{self.title}", url=f"{self.url}", description="", color=0xfaa61a)
        embed.set_thumbnail(url=f"{self.thumbnail}")
        embed.add_field(name="Price", value=f"{self.price}$", inline=True)
        embed.add_field(name="Location",
                        value=f"`{self.location}`", inline=True)
        embed.add_field(name="Condition",
                        value=f"`{self.condition}`", inline=True)
        utils.async_from_sync(bot.get_event_loop(),
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
                item = None
                if Filters.filter_response_items(search, i):
                    item = Item.item_from_data(i)

                if not item:
                    continue

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
    def __init__(self, url, channel_id,
                 newest_start_time=utils.datetime_to_str_ebay(datetime.utcnow())):
        self.url = url
        self.ebay_site, self.keywords, self.filters = Search.get_search_from_url(
            url)
        self.channel_id = channel_id
        self.newest_start_time = newest_start_time

    def add_to_list(self):
        search_list.append(self)
        bot.update_get_items_interval()

    def formatted_search(self, widths):
        return f"{self.query: <{widths[1]}}  {self.min_price+'$' : >{widths[2]}}  {self.max_price+'$' : >{widths[3]}}"

    def set_newest_start_time_filter(self):
        self.filters['StartTimeFrom'] = self.newest_start_time

    def get_filters(self):
        self.set_newest_start_time_filter()
        return self.filters.copy()

    async def display(self, channel_id, message):
        channel = bot.get_bot().get_channel(channel_id)

        embed = discord.Embed(
            title=message, description="", color=0x17c3b2)
        embed.add_field(name="Keywords", value=f"{self.keywords}", inline=True)
        embed.add_field(name="Ebay site",
                        value=f"`{self.ebay_site}`", inline=True)
        embed.add_field(
            name="Filters", value=f"[See on ebay]({self.url})", inline=True)
        await channel.send(embed=embed)

    @staticmethod
    def get_search_from_url(url):
        parsed = urlparse.urlparse(url)
        query = urlparse.parse_qs(parsed.query)

        # UNSUPPORTED EBAY SITES: ebay.cn / ebay.com.tw / ebay.co.th
        ebay_site = parsed.hostname.replace('www.', '')
        ebay_site = mapping.map_ebay_site_to_id(ebay_site)

        keywords = query.get('_nkw')[0] if query.get('_nkw') else None

        filters = Filters.get_from_query(query, ebay_site)

        return ebay_site, keywords, filters

    @staticmethod
    async def get_searches_table(list, page):
        # FIXLATER: Doesn't look good on mobile devices.
        fields = {'#': '', 'Keywords': '', 'Ebay site': ''}
        clean_page_count = {'#': 0, 'Keywords': 0, 'Ebay site': 0}
        page_counter = [clean_page_count.copy()]
        i = 0

        while i < len(list):
            search = list[i]
            page_index = len(page_counter)-1

            temp_fields = {
                '#': f"\u200b\n{i}\n",
                'Keywords': f"\u200b\n**[{search.keywords}]({search.url})**\n",
                'Ebay site': f"\u200b\n{search.ebay_site.lower()}\n",
            }
            page_counter[page_index]['#'] += len(temp_fields.get('#'))
            page_counter[page_index]['Keywords'] += len(
                temp_fields.get('Keywords'))
            page_counter[page_index]['Ebay site'] += len(
                temp_fields.get('Ebay site'))

            len_check = any(
                [k for k in page_counter[page_index].values() if k > MAX_CHARACTERS])

            if not len_check and len(page_counter) == page:
                fields = {k: (v+temp_fields.get(k))
                          for (k, v) in fields.items()}
            elif len_check:
                # It keeps going for the sake of counting pages.
                # I know it's inefficient :)
                page_counter.append(clean_page_count.copy())
                i -= 1

            i += 1

        return fields, len(page_counter)

    @staticmethod
    async def get_list_display_embed(list=search_list, page=1, title="Searches", color=0x1098f7, show_nrs=True):
        fields, total_pages = await Search.get_searches_table(list, page)

        if not any({v for v in fields.values() if v}):
            return None

        embed = discord.Embed(
            title=title, description="Click on a search to open it on ebay and see it's filters", color=color)

        for name, value in fields.items():
            if (name != '#' or show_nrs):
                embed.add_field(name=name, value=value, inline=True)

        embed.set_footer(text=f"\u200b\n< {page} / {total_pages} >"
                              "\n\n"
                              f"Fetching items every {bot.get_items_interval_str()}")
        return embed

    @staticmethod
    async def save_searches():
        data_s = {}
        data_s['searches'] = []
        for search in search_list:
            data_s["searches"].append(
                {'url': search.url,
                 'channel_id': f"{search.channel_id}"})
            await asyncio.sleep(0.01)
        data.save(data_s)

    @staticmethod
    def read_searches():
        try:
            json_s = data.read()
            data_s = json.loads(json_s)
            for q in data_s['searches']:
                search = Search(q['url'], int(q['channel_id']))
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

                temp_filters = self.get_filters()

                while temp_filters:
                    try:
                        filters, temp_filters = temp_filters.get_for_request()

                        api = Finding(domain=settings.get("domain"),
                                      appid=settings.get("appid"),
                                      version=settings.get("version"),
                                      config_file=None,
                                      site_id=self.ebay_site)

                        api_request = {'keywords': f'{self.keywords}',
                                       'itemFilter': filters,
                                       'sortOrder': 'StartTimeNewest'}

                        response = api.execute(
                            'findItemsAdvanced', api_request)

                        # # FIXME: Uncomment for debug only
                        # print(f"{response.headers}  :  {response.content}")

                        Item.items_from_response(self, response)
                    except ConnectionError:
                        pass
                    except AttributeError as e:
                        print(f"Exception in get_items: {e}")
                        pass
                    except Exception as e:  # idc just stop breaking
                        print(f"Exception in get_items: {e}")
                        pass

            except IndexError:
                time.sleep(0.01)
                continue

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

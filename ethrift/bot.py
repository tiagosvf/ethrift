# External modules
from discord import embeds
import yaml
import math
import discord
import asyncio
from discord.ext import commands, tasks
from datetime import datetime

# Internal modules
import utils
import ebay


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


active_time = [datetime(1900, 1, 1, 0, 0, 0), datetime(1900, 1, 1, 0, 0, 0)]

token = ""
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
                                           "\n`!add <url>` › Add search from URL"
                                           "\n`!del <search numbers (#) separated by spaces>` › Remove searches"
                                           "\n`!searches`, `!list` or `!lst` `[page]` › List all currently active searches"
                                           "\n"
                                           "\n`!active` › Check the bot's active hours"
                                           "\n`!active from <hh:mm> to <hh:mm>` › Set the bot's active hours"
                                           "\n"
                                           "\n`!kill` › Shut down the bot", inline=True)
    await ctx.send(embed=embed)


@bot.command(aliases=["queries", "list", "lst"])
async def searches(ctx, page=1):
    result = await ebay.Search.get_list_display_embed(page=page, title="List of searches")
    if result:
        await ctx.send(embed=result)
    else:
        await ctx.send("```You have not added any searches.\nAdd one using !add <\"query keywords\"> <min_price> <max_price>```")


@bot.command()
async def add(ctx, url):
    if hasattr(bot.get_channel(ctx.channel.id), 'recipient'):
        await ctx.send("```Not possible to use bot from direct messages yet.\nInvite me to a channel and add searches from there please.```")
        return

    search = ebay.Search(url, ctx.channel.id)
    search.add_to_list()
    await ebay.Search.save_searches()
    await search.display(ctx.channel.id, "Added search:")


@bot.command(aliases=["del", "rm", "rem", "remove"])
async def delete(ctx, *indexes):
    search_list = ebay.get_search_list()
    indexes = list(indexes)
    removed_searches = []
    for index in sorted(indexes, reverse=True):
        try:
            removed_searches.append(search_list.pop(int(index)))
        except IndexError:
            indexes.remove(index)
    result = await ebay.Search.get_list_display_embed(list=removed_searches,
                                                      title="Removed searches",
                                                      color=0xed474a,
                                                      show_nrs=False)
    await ebay.Search.save_searches()
    update_get_items_interval()
    await ctx.send(embed=result)


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
            await ctx.send(f"```Active time changed\nI will be looking for items {utils.get_active_time_str(active_time)} every {get_items_interval_str()}```")
        except ValueError:
            await ctx.send("```Invalid time format\nTime should be in HH:MM format like 08:30```")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.CommandError):
        print(f"Error: {error}")
        await ctx.send("```An error occured.\nUse !help to make sure you used the command correctly.```")


@tasks.loop(seconds=18)
async def get_items():
    if(utils.is_time_between(active_time[0].time(), active_time[1].time())):
        await ebay.Search.get_items_list()


def get_items_interval_str():
    return f"{get_items.minutes} minutes and {get_items.seconds} seconds"


def get_event_loop():
    return loop


def get_bot():
    return bot


def read_settings():
    with open(utils.get_file_path("settings.yaml")) as file:
        _settings = yaml.safe_load(file)

        global token
        token = _settings["discord"]["token"]


def start_get_items():
    get_items.start()


def update_get_items_interval():
    seconds = utils.seconds_between_times(active_time[0], active_time[1])
    seconds = 86400 if seconds == 0 else seconds
    seconds = math.ceil((seconds/ebay.get_max_calls())
                        * len(ebay.get_search_list()))
    minutes, seconds = divmod(seconds, 60)
    get_items.change_interval(minutes=minutes, seconds=seconds)


def main():
    read_settings()
    bot.run(token)

# External modules
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
    """Check if the bot is online"""
    await ctx.send("Pong!")


@bot.command()
async def kill(ctx):
    """Shuts down the bot
    
    Will remove soon
    """
    await ctx.send("Goodbye!")
    await bot.logout()


@bot.command(aliases=["commands", "help"])
async def cmd(ctx):
    """Shows list of commands and more information"""
    embed = discord.Embed(title="\u200b\nI am a simple bot that warns you about new items in eBay searches",
                          description="\u200b\u200b", color=0xc200a8)
    embed.set_author(name="ethrift by @tiagosvf", url="https://github.com/tiagosvf",
                     icon_url="https://avatars0.githubusercontent.com/u/25352856?s=460&u=f5b0c682e7634580340e2fea35bce3764686e02e&v=4")
    embed.add_field(name="Commands", value="`!help`, `!cmd` or `!commands` › Show this message"
                                           "\n`!ping` › Check if bot is online"
                                           "\n"  # TODO: Create a wiki and add information about supported filters
                                           "\n`!add <url>` › Add search from URL (read the [wiki](https://github.com/tiagosvf/ethrift-py/wiki) for [supported filters](https://github.com/tiagosvf/ethrift-py/wiki/Usage#supported-filters))"
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
    """Lists the current active searches in the selected page.
    Shows page one if no page is set
    """
    result = await ebay.Search.get_list_display_embed(page=page, title="List of searches")
    if result:
        await ctx.send(embed=result)
    else:
        await ctx.send("```You have not added any searches.\nTo add one go to ebay, make a search, copy the URL and use !add <url>```")


@bot.command()
async def add(ctx, url):
    """Adds a search from the requested URL

    Usage: !add <url>
    Example: !add https://www.ebay.co.uk/sch/i.html?_nkw=selected+ambient+works+cd&LH_TitleDesc=0
    Result: adds search for "selected ambient works cd" in the EBAY-UK website
    """
    if hasattr(bot.get_channel(ctx.channel.id), 'recipient'):
        await ctx.send("```Not possible to use bot from direct messages yet.\nInvite me to a channel and add searches from there please.```")
        return

    result = await ebay.Search.add_from_url(url, ctx.channel.id)
    if result:
        await ctx.send(embed=result)
    else:
        await ctx.send("```The provided URL seems to be invalid.\nGo to ebay, make a search by keywords, and copy the URL in your browser's address bar.```")


@bot.command(aliases=["del", "rm", "rem", "remove"])
async def delete(ctx, *indexes):
    """Removes the searches in the given indexes

    Usage: !del <indexes>
    Example: !del 0 3 7
    Result: Deletes searches in indexes 0, 3 and 7
    """
    indexes = list(indexes)
    result = await ebay.Search.delete(indexes)
    if result:
        await ctx.send(embed=result)


@bot.command()
async def active(ctx,  *args):
    """Display or sets the active time for the bot

    Usage: !active from <hh:mm> to <hh:mm>
    Example: !active from 10:30 to 00:00
    Result: Sets the active to be from 10:30 to 00:00

    OR

    Usage: !active
    Result: Displays the current active time
    """
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
    """Handles uncaught exceptions when using commands"""
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.CommandError):
        print(f"Error: {error}")
        await ctx.send("```An error occured.\nUse !help to make sure you used the command correctly.```")


@tasks.loop(seconds=18)
async def get_items():
    """get_items task. Periodically runs through searches and adds them to
    the queue to look for new items"""
    if(utils.is_time_between(active_time[0].time(), active_time[1].time())):
        await ebay.Search.get_items_list()


def get_items_interval_str():
    """Returns get_items interval as a formatted string to display"""
    return f"{get_items.minutes} minutes and {get_items.seconds} seconds"


def get_event_loop():
    """Returns the current event loop"""
    return loop


def get_bot():
    """Returns the Discord bot oject"""
    return bot


def read_settings():
    """Gets the Discord bot token from the settings.yaml"""
    with open(utils.get_file_path("settings.yaml")) as file:
        _settings = yaml.safe_load(file)

        global token
        token = _settings["discord"]["token"]


def start_get_items():
    """Starts the get_items task"""
    get_items.start()


def update_get_items_interval():
    """Updates the interval of the get_items task"""
    seconds = utils.seconds_between_times(active_time[0], active_time[1])
    seconds = 86400 if seconds == 0 else seconds
    seconds = math.ceil((seconds/ebay.get_max_calls())
                        * len(ebay.get_search_list()))
    minutes, seconds = divmod(seconds, 60)
    get_items.change_interval(minutes=minutes, seconds=seconds)


def main():
    read_settings()
    bot.run(token)

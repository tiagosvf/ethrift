import math
import os
import asyncio
from datetime import datetime


def async_from_sync(loop, function, *args, **kwargs):
    """
    Wrapper to allow calling async functions from sync
    and running them in set event loop

    Keyword Arguments:
        loop               -- event loop to run function in
        function           -- function to be ran
        *args, **kwargs    -- arguments to be passed to the function
    """
    res = function(*args, **kwargs)
    asyncio.run_coroutine_threadsafe(res, loop).result()


def get_file_path(filename):
    """Receives a relative file path and returns the absolute one"""
    return os.path.join(os.path.dirname(__file__), filename)


def is_time_between(begin_time, end_time, check_time=None):
    """Checks if a datetime is between two others
    
    Keyword Arguments:
        begin_time         -- datetime where interval starts
        end_time           -- datetime where interval ends
        check_time         -- datetime to check

    Return Value:
    True if check_time is between begin_time and end_time.
    False otherwise
    """
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:
        return check_time >= begin_time or check_time <= end_time


def seconds_between_times(begin_datetime, end_datetime):
    """Returns the number of seconds between two given datetime objects"""
    if begin_datetime > end_datetime:
        return 86400 - (begin_datetime-end_datetime).seconds
    else:
        return (end_datetime-begin_datetime).seconds


def get_active_time_str(active_time):
    """Returns the bot's active time as a formatted string for display"""
    if (active_time[0]-active_time[1]).seconds == 0:
        return "all day"
    else:
        return f"from {str(active_time[0].time())[0:5]} to {str(active_time[1].time())[0:5]}"


def datetime_to_str_ebay(_datetime):
    """Returns the given datetime as a ISO formatted string"""
    return f"{_datetime.year:04d}-{_datetime.month:02d}-{_datetime.day:02d}T{_datetime.hour:02d}:{_datetime.minute:02d}:{_datetime.second:02d}.000Z"


def str_to_datetime_ebay(str):
    """Returns a datetime object from an ISO format date string"""
    return datetime.strptime(str[:-5], "%Y-%m-%dT%H:%M:%S")


def number_length(n):
    """Returns the length in digits of a the number"""
    if n > 0:
        return int(math.log10(n))+1
    elif n == 0:
        return 1
    else:
        return int(math.log10(-n))+2

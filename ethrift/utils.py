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


def datetime_to_iso(_datetime):
    """Returns the given datetime as a ISO formatted string"""
    return f"{_datetime.year:04d}-{_datetime.month:02d}-{_datetime.day:02d}T{_datetime.hour:02d}:{_datetime.minute:02d}:{_datetime.second:02d}.000Z"


def iso_to_datetime(str):
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

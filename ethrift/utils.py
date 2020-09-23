import math
import os
from datetime import datetime


def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def is_time_between(begin_time, end_time, check_time=None):
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:
        return check_time >= begin_time or check_time <= end_time


def seconds_between_times(begin_datetime, end_datetime):
    if begin_datetime > end_datetime:
        return 86400 - (begin_datetime-end_datetime).seconds
    else:
        return (end_datetime-begin_datetime).seconds


def get_items_interval_str(get_items):
    return f"{get_items.minutes} minutes and {get_items.seconds} seconds"


def get_active_time_str(active_time):
    if (active_time[0]-active_time[1]).seconds == 0:
        return "all day"
    else:
        return f"from {str(active_time[0].time())[0:5]} to {str(active_time[1].time())[0:5]}"


def datetime_to_str_ebay(_datetime):
    return f"{_datetime.year:04d}-{_datetime.month:02d}-{_datetime.day:02d}T{_datetime.hour:02d}:{_datetime.minute:02d}:{_datetime.second:02d}.000Z"


def str_to_datetime_ebay(str):
    return datetime.strptime(str[:-5], "%Y-%m-%dT%H:%M:%S")


def number_length(n):
    if n > 0:
        return int(math.log10(n))+1
    elif n == 0:
        return 1
    else:
        return int(math.log10(-n))+2
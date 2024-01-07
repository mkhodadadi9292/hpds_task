import os
from datetime import datetime

# import pytz

# _environment_timezone = pytz.timezone(os.environ.get('TZ'))


def now():
    return datetime.now()


def fromtimestamp(timestamp: float):
    return datetime.fromtimestamp(timestamp)




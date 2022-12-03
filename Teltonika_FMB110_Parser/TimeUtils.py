import datetime


def readTime():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def unixToLocal(unix_time):
    time = datetime.datetime.fromtimestamp(unix_time / 1000)
    return f"{time:%Y-%m-%d %H:%M:%S}"

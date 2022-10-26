import os
import datetime
def modification_date(filename):
    if os.path.exists(filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)
    else:
        return ""
'''
Created on Jan 16, 2024

@author: Dennis
'''

from datetime import datetime, timedelta
from os import getenv

'''
Return a range of columns from a string
'''
def getColumn(astr : str, first : int, last : int) -> str:
    return astr[first-1:last].strip()

def putColumn(astr : str, add : str, first : int, last : int) -> str:
    astr[first-1:last] = add
    return astr

def toTime(date_str : str, time_str : str) -> datetime:
    result = datetime.strptime(date_str + ' ' + time_str, '%d-%b-%y %H:%M:%S')
    return result

def timeDeltaToMinutesSeconds(delta : timedelta) -> str:
    seconds = delta.total_seconds()
    result = "%d:%02d" % (seconds//60, seconds % 60)
    return result

def get_full_path(file_name):
    path = getenv("MORF_DATA")
    if path:
        return path + file_name
    
    return file_name
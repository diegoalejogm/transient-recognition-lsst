from datetime import datetime
import astropy.time as astime

def time(func, *args, **kwargs):
    startTime = datetime.now()
    x = func(*args, **kwargs)
    print(datetime.now() - startTime)
    return x

def mjd_to_datetime(mjd):
    t = astime.Time(mjd, format='mjd')
    return t.datetime
    
def datetime_to_mjd(datetime):
    t = astime.Time(datetime)
    return t.mjd
import numpy as np

def __datetime_diff_to_int_timedelta__(ss_date):
    '''
    Convert datetime series to integer timedelta
    '''
    return ss_date.diff().dt.total_seconds() / 3600

def __percentile_diff_ratio__(ss_mag, p):
    '''
    Calculate ratio of flux percentiles (p1 - p2) / (95th - 5th).
    p1: Percentile p. p2: Percentile 100-p.
    '''
    num = ss_mag.quantile(p) - ss_mag.quantile(100-p)
    denom = ss_mag.quantile(95) - ss_mag.quantile(5)
    return num/denom

def skew(ss_mag):
    '''
    Skew of the fluxes.
    '''
    return series_mag.skew()

def kurtosis(ss_mag):
    '''
    Kurtosis of the fluxes, reliable down to a small number of epochs.
    '''
    return series_mag.kurtosis()

def std(ss_mag):
    '''
    Standard deviation of the fluxes.
    '''
    return series_mag.std()

def beyond1st(ss_mag, ss_magerr):
    '''
    Percentage of points beyond one st. dev. from the weighted mean.
    '''
    N = ss_mag.shape[0]
    weighted_mean = (ss_mag / ss_magerr).mean()
    stdev = std(ss_mag)
    ss_beyond1st = ss_mag[(ss_mag - stdev).abs() > weighted_mean]
    return ss_beyond1st.shape[0] / N

def amplitude(ss_mag):
    '''
    Half the difference between the maximum and the minimum magnitudes.
    '''
    return ( ss_mag.max() - ss_mag.min() ) / 2.

def max_slope(ss_mag, ss_date):
    '''
    Maximum absolute flux slope between two consecutive observations.
    '''
    ss_timedelta = __datetime_diff_to_int_timedelta__(ss_date.diff())
    return (ss_mag.diff() / ss_timedelta).abs().max()

def median_absolute_deviation(ss_mag):
    '''
    Median discrepancy of the fluxes from the median flux.
    '''
    return ss_mag.mad()

def pair_slope_trend(ss_mag, ss_date):
    '''
    Percentage of all pairs of consecutive flux measurements that have positive slope.
    '''
    N = ss_mag.shape[0]
    ss_timedelta = __datetime_diff_to_int_timedelta__(ss_date.diff())
    ss_slopes = (ss_mag.diff() / ss_timedelta)
    return ss_slopes[ss_slopes > 0].shape[0] / N

def linear_trend(ss_mag, ss_date):
    '''
    Slope of a linear fit to the light curve fluxes.
    '''
    ss_date_diff = ss_date - dt.datetime(1970,1,1)
    ss_timedelta = __datetime_to_int_timedelta__(ss_date_diff)
    m, b = np.polyfit(ss_timedelta, ss_mag, 1)
    return m

def flux_percentile_ratio_mid20(ss_mag):
    '''
    Ratio of flux percentiles (60th - 40th) over (95th - 5th).
    '''
    return __percentile_diff_ratio__(ss_mag, 60)

def flux_percentile_ratio_mid35(ss_mag):
    '''
    Ratio of flux percentiles (67.5th - 32.5th) over (95th - 5th).
    '''
    return __percentile_diff_ratio__(ss_mag, 67.5)

def flux_percentile_ratio_mid50(ss_mag):
    '''
    Ratio of flux percentiles (75th - 25th) over (95th - 5th).
    '''
    return __percentile_diff_ratio__(ss_mag, 75)

def flux_percentile_ratio_mid65(ss_mag):
    '''
    Ratio of flux percentiles (82.5th - 17.5th) over (95th - 5th).
    '''
    return __percentile_diff_ratio__(ss_mag, 82.5)

def flux_percentile_ratio_mid80(ss_mag):
    '''
    Ratio of flux percentiles (90th - 10th) over (95th - 5th).
    '''
    return __percentile_diff_ratio__(ss_mag, 90)

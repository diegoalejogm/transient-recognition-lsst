import numpy as np

def __datetime_diff_to_int_timedelta__(ss_date):
    '''
    Convert datetime series to integer timedelta
    '''
    return ss_date.diff().dt.total_seconds() / 3600

def __mag_to_flux__(ss_mag):
    return 10. ** (-ss_mag)

def __flux_to_mag__(ss_flux):
    return -np.log10(ss_flux)

def __percentile_diff_ratio__(ss_flux, p):
    '''
    Calculate ratio of flux percentiles (p1 - p2) / (95th - 5th).
    p1: Percentile p. p2: Percentile 100-p.
    '''
    num = ss_flux.quantile(p) - ss_flux.quantile(100-p)
    denom = ss_flux.quantile(95) - ss_flux.quantile(5)
    return num/denom

def __stetson_sigmas__(ss_mag, ss_magerr):
    '''
    Calculates the relative errors (sigmas) for stetson measurements.
    '''
    sigmas = np.sqrt(n / (n - 1)) * (ss_mag - ss_mag.mean()) / ss_magerr
    return sigmas

def skew(ss_flux):
    '''
    Skew of the fluxes.
    '''
    return ss_flux.skew()

def kurtosis(ss_flux):
    '''
    Kurtosis of the fluxes, reliable down to a small number of epochs.
    '''
    return ss_flux.kurtosis()

def std(ss_flux):
    '''
    Standard deviation of the fluxes.
    '''
    return ss_flux.std()

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

def max_slope(ss_flux, ss_date):
    '''
    Maximum absolute flux slope between two consecutive observations.
    '''
    ss_timedelta = __datetime_diff_to_int_timedelta__(ss_date.diff())
    return (ss_flux.diff() / ss_timedelta).abs().max()

def median_absolute_deviation(ss_flux):
    '''
    Median discrepancy of the fluxes from the median flux.
    '''
    return ss_flux.mad()

def pair_slope_trend(ss_flux, ss_date):
    '''
    Percentage of all pairs of consecutive flux measurements that have positive slope.
    '''
    N = ss_flux.shape[0]
    ss_timedelta = __datetime_diff_to_int_timedelta__(ss_date.diff())
    ss_slopes = (ss_flux.diff() / ss_timedelta)
    return ss_slopes[ss_slopes > 0].shape[0] / N

def linear_trend(ss_flux, ss_date):
    '''
    Slope of a linear fit to the light curve fluxes.
    '''
    ss_date_diff = ss_date - dt.datetime(1970,1,1)
    ss_timedelta = __datetime_to_int_timedelta__(ss_date_diff)
    m, b = np.polyfit(ss_timedelta, ss_flux, 1)
    return m

def flux_percentile_ratio_mid20(ss_flux):
    '''
    Ratio of flux percentiles (60th - 40th) over (95th - 5th).
    '''
    return __percentile_diff_ratio__(ss_flux, 60)

def flux_percentile_ratio_mid35(ss_flux):
    '''
    Ratio of flux percentiles (67.5th - 32.5th) over (95th - 5th).
    '''
    return __percentile_diff_ratio__(ss_flux, 67.5)

def flux_percentile_ratio_mid50(ss_flux):
    '''
    Ratio of flux percentiles (75th - 25th) over (95th - 5th).
    '''
    return __percentile_diff_ratio__(ss_flux, 75)

def flux_percentile_ratio_mid65(ss_flux):
    '''
    Ratio of flux percentiles (82.5th - 17.5th) over (95th - 5th).
    '''
    return __percentile_diff_ratio__(ss_flux, 82.5)

def flux_percentile_ratio_mid80(ss_flux):
    '''
    Ratio of flux percentiles (90th - 10th) over (95th - 5th).
    '''
    return __percentile_diff_ratio__(ss_flux, 90)

def percent_amplitude(ss_flux):
    '''
    Largest percentage difference between either the max or min magnitude and the median.
    '''
    median = ss_flux.median()
    max_diff = (ss_flux.max() - median).abs()
    min_diff = ss_flux.min() - median).abs()
    return np.max(max_diff, min_diff) / median

def median_buffer_range_percentage(ss_flux):
    '''
    Percentage of fluxes within 10% of the amplitude from the median.
    '''
    N = ss_flux.shape[0]
    median = ss_flux.median()
    mbf_list = ss_flux[(ss_flux - median).abs() < .1 * median]
    return mbf_list / float(N)

def percent_difference_flux_percentile(ss_flux):
    '''
    Ratio of (95th - 5th) flux percentile over the median flux.
    '''
    return ( ss_flux.quantile(95) - ss_flux.quantile(5) ) / ss_flux.median()

def stetson_j(ss_mag, ss_magerr, ss_date, exponential=False):
    '''
    The Welch-Stetson J variability index (Stetson 1996).
    A robust standard deviation.
    Optional exponential weighting scheme (Zhang et al. 2003) taking successive pairs in time order.
    NOTE: ss_flux must be ordered by it's corresponding date in ss_date.
    '''
    n = float(ss_mag.shape[0])
    if n <= 1: return 0
    # Calculate sigmas: Relative Errors
    sigmas = __stetson_sigmas__(ss_mag, ss_magerr)
    # Calculate weights
    w = np.ones(n)
    if exponential:
        # Calculate mean dt: delta-time
        dt = __datetime_diff_to_int_timedelta__(ss_date.diff()).mean()
        # Re-calculate Weights
        w = np.exp(-ss_mag.diff() / dt)
    # Calculate p: product of residuals
    p = sigmas * sigmas.shift(1)
    # Calculate Stetson J measuerement
    stetson_j = (w * np.sign(p) * p.abs().pow(1./2)).sum() / w.sum()
    return stetson_j

def stetson_k(ss_mag):
    '''
    Welch-Stetson variability index K (Stetson 1996).
    Robust kurtosis measure.
    '''
    n = float(ss_mag.shape[0])
    if n <= 1: return 0
    # Calculate sigmas: Relative Errors
    sigmas = __stetson_sigmas__(ss_mag, ss_magerr)
    # Calculate Stetson K measuerement
    stetson_k = sigmas.abs().mean() / sigmas.pow(2.).mean().pow(1./2)
    return stetson_k

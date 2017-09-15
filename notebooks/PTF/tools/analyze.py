import pandas as pd
from . import constants
from astropy.table import Table
import os
from . import io

# REQUIRES ADDING 'lighcurve_path' COL TO INPUT DataFrame
def lightcurve_real_nobs(obj_cat_df, obj_light_curves_df, limit=None, append_series=False):
    real_nobs = []
    for i, obj in obj_cat_df.iterrows():
        if limit and i == limit:
            break
        else:
            lightcurve_df = obj_light_curves_df[obj_light_curves_df['oid'] == obj['oid']]
            real_nobs.append(lightcurve_df.shape[0])
    if append_series:
        obj_cat_df['real_nobs'] = pd.Series(real_nobs)
    return real_nobs

# REQUIRES ADDING 'lighcurve_path' COL TO INPUT DataFrame
def consolidate_light_curves(obj_cat_df, transient=False, limit=None):
    outdir = constants.DIR_LIGHTCURVES_RED_CONSOLIDATED + ('transient/' if transient else 'permanent/')
    io.makedir(outdir)
    filename = 'consolidated.pickle'
    filepath = outdir + filename
    if not io.file_exists(filename, outdir):
        consolidated_df = pd.DataFrame()
        for i, obj in obj_cat_df.iterrows():
            if limit and i == limit:
                break
            else:
                lightcurve_df = Table.read(obj['lightcurve_path'], format='ascii').to_pandas()
                consolidated_df = consolidated_df.append(lightcurve_df, ignore_index=True)
        consolidated_df.to_pickle(filepath)
    return filepath
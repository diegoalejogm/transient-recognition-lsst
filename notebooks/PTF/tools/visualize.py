from plotly.offline import init_notebook_mode
import plotly.graph_objs as go
from . import constants, io, time
from astropy.table import Table
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

init_notebook_mode(connected=True)

def light_curve_scatter(obj_light_curve_df, marker_size=None):
    if obj_light_curve_df.shape[0] == 0:
        plt.scatter([], [], s=marker_size)
    else:
        plt.scatter(time.mjd_to_datetime(obj_light_curve_df.obsmjd), obj_light_curve_df.mag_autocorr, s=marker_size)

def light_curve_interactive_scatter(obj_light_curve_df, transient=None, mode='markers', name=None):
    if obj_light_curve_df.shape[0] == 0:
        scatter = go.Scatter(x=pd.Series([]), y=pd.Series([]), name=[])
    else:
        scatter = go.Scatter(
            mode=mode,
            x=pd.Series(time.mjd_to_datetime(obj_light_curve_df['obsmjd'])),
            y=obj_light_curve_df.mag_autocorr,
            name= name if name else obj_light_curve_df.oid[0]
        )
    return scatter

def generate_individual_light_curve_scatters(obj_cat_df, obj_light_curves_df, is_transient, limit=None, append_df=True):
    filepaths = []
    outdir = constants.DIR_LIGHTCURVES_RED_SCATTERS + ('transient/' if is_transient else 'permanent/')
    io.makedir(outdir)
    
    for i, row in obj_cat_df.iterrows():
        if limit and i == limit:
            break
        else:
            oid = row['oid']
            filename = '{}.png'.format(oid)
            filepath = outdir + filename
            if not io.file_exists(filename, outdir):
                light_curve_df = obj_light_curves_df[obj_light_curves_df['oid'] == oid]
                light_curve_scatter(light_curve_df)
                plt.savefig(filepath, dpi=120)
                plt.close()
                filepaths.append(filepath)
    if append_df:
        obj_cat_df['scatter_path'] = np.nan
        obj_cat_df['scatter_path'] = pd.Series(filepaths)
    return pd.Series(filepaths)

### This method has the limitation of max. 100 freely created images from plotly
'''
def individual_light_curve_images(obj_cat_df, transient, limit=None, name=None):
    filepaths = []
    outdir = constants.DIR_LIGHTCURVES_RED_SCATTERS + ('transient/' if transient else 'permanent/')
    io.makedir(outdir)
    py.sign_in('diegoalejogm', 'N0lGGDV0PmKoW4LpSVyI') # Replace the username, and API key with your credentials.
    for i, obj in obj_cat_df.iterrows():
        if limit and i == limit:
            break
        else:
            filename = '{}.png'.format(obj['oid'])
            filepath = outdir + filename
            if not io.file_exists(filename, outdir):
                light_curve_df = Table.read(obj['lightcurve_path'], format='ascii').to_pandas()
                light_curve_scat = light_curve_scatter(light_curve_df)
                figure = go.Figure(data=[light_curve_scat])
                py.image.save_as(figure, filename=filepath)
                filepaths.append(filepath)
    return filepaths
'''

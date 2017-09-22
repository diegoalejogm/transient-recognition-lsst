from plotly.offline import init_notebook_mode
import plotly.graph_objs as go
from . import constants, io, time
from astropy.table import Table
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

init_notebook_mode(connected=True)

def light_curve_interactive_scatter(obj_light_curve_df, mode='markers', name=None):
    if obj_light_curve_df.shape[0] == 0:
        scatter = go.Scatter(x=pd.Series([]), y=pd.Series([]), name=[])
    else:
        scatter = go.Scatter(
            mode=mode,
            x=pd.Series(time.mjd_to_datetime(obj_light_curve_df['MJD'])),
            y=obj_light_curve_df.Mag,
            name= name if name else obj_light_curve_df.InputID.iloc[0]
        )
    return scatter

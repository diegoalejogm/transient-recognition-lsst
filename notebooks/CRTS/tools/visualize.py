from . import time, io
from . import constants as k 
from plotly.offline import init_notebook_mode
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns

init_notebook_mode(connected=True)

def light_curve_interactive_scatter(obj_light_curve_df, mode='markers', name=None):
    if obj_light_curve_df.shape[0] == 0:
        scatter = go.Scatter(x=pd.Series([]), y=pd.Series([]), name=[])
    else:
        scatter = go.Scatter(
            mode=mode,
            x=pd.Series(time.mjd_to_datetime(obj_light_curve_df.MJD)),
            y=obj_light_curve_df.Mag,
            name= name if name else obj_light_curve_df.ObjectID.iloc[0]
        )
    return scatter


def light_curve(df, filename, mode='markers'):
    io.makedir(k.DIR_IMAGES_SCATTERS)
    plot_df = df.plot(x='Date', y='Mag', style='.', ms=.6, figsize=(20,15))
    plot_df.autoscale(tight=False)
    plt.savefig(k.DIR_IMAGES_SCATTERS + filename + '.png', dpi=150)
    plt.close(plot_df.get_figure())


def combined_light_curves(df_lc, n_obj, obj_type, min_obs=None, filtre=None, random_state=182):
    df_lc = df_lc.copy()
    np.random.seed(random_state)
    # Sample data
    if min_obs: 
        s_grouped = df_lc.groupby(['ObjectID']).count()['ID']
        valid_obs = s_grouped[s_grouped >= min_obs].index.tolist()
        df_lc = df_lc[df_lc.ObjectID.isin(valid_obs)]
    sample_obj_ids = np.random.choice(df_lc.ObjectID.unique(), n_obj, replace=False)
    df_lc_sample = df_lc[df_lc.ObjectID.isin(sample_obj_ids)].copy()
    # Separate LCs into seasons
    for obj_id in sample_obj_ids:
        prev_MJD, season_index = None, -1
        for lc_row_index, lc_row in df_lc_sample[df_lc_sample.ObjectID == obj_id].sort_values(['MJD']).iterrows():
            current_MJD = lc_row.MJD
            if prev_MJD == None or (current_MJD - prev_MJD) >= 180:
                prev_MJD, season_index = current_MJD, season_index+1
            df_lc_sample.loc[lc_row_index, 'Season'] = season_index
    df_lc_sample['Season'] = df_lc_sample['Season'].astype(int)
    
    figsize = (20,8)
    # Draw LCs for each object, using all seasons
    __combined_light_curves_joint__(obj_type, sample_obj_ids, df_lc_sample, figsize)
    # Draw LCs for each object, per season
    __combined_light_curves_per_season__(obj_type, sample_obj_ids, df_lc_sample, figsize)

        
def __combined_light_curves_joint__(obj_type, sample_obj_ids, df_lc_sample, figsize):
    curves_season_out_dir = k.DIR_IMAGES_CURVES + str(obj_type) + '/all-seasons/'
    io.makedir(curves_season_out_dir)
    for obj_id in sample_obj_ids:
        for season_num in sorted(df_lc_sample.Season.unique()):
            filename = curves_season_out_dir
            df_current = df_lc_sample[(df_lc_sample.ObjectID == obj_id) & (df_lc_sample.Season == season_num)]
            if df_current.empty: continue
            # Resample data using mean
            s_resampled = df_current.resample('D',on='Date').mean()['Mag']
            plot_resampled = s_resampled.plot(figsize=figsize, style='.')
            plot_resampled.autoscale(tight=False)
            # Interpolate data using splines
            n_rows = s_resampled[s_resampled.notnull()].shape[0]
            interpolation_order = 3 if n_rows >= 5 else (2 if n_rows == 4 else 1)
            s_interpolated = s_resampled.interpolate(method='spline', order=interpolation_order)
            # Plot interpolated data
            plot_interpolated = s_interpolated.plot(figsize=figsize, color=plot_resampled.get_lines()[-1].get_color())
            plot_interpolated.autoscale(tight=False)
            # Save plot
        plot_interpolated.get_figure().savefig(filename + '{}.png'.format(obj_id), dpi=110)
        plot_interpolated.set_ylim(8, 24)
        plot_interpolated.get_figure().savefig(filename + 'full_{}.png'.format(obj_id), dpi=110)
        # Close plot
        plt.close(plot_interpolated.get_figure())
        
def __combined_light_curves_per_season__(obj_type, sample_obj_ids, df_lc_sample, figsize):
    for season_num in sorted(df_lc_sample.Season.unique()):
        curves_season_out_dir = k.DIR_IMAGES_CURVES + str(obj_type) + '/season{}/'.format(season_num)
        io.makedir(curves_season_out_dir)
        for obj_id in sample_obj_ids:
            filename = curves_season_out_dir + '{}.png'.format(obj_id)
            df_current = df_lc_sample[(df_lc_sample.ObjectID == obj_id) & (df_lc_sample.Season == season_num)]
            if df_current.empty: continue
            # Resample data using mean
            s_resampled = df_current.resample('D',on='Date').mean()['Mag']
            plot_resampled = s_resampled.plot(figsize=figsize, style='.')
            plot_resampled.autoscale(tight=False)
            n_rows = s_resampled[s_resampled.notnull()].shape[0]
            # Interpolate data using splines
            interpolation_order = 3 if n_rows >= 5 else (2 if n_rows == 4 else 1)
            s_interpolated = s_resampled.interpolate(method='spline', order=interpolation_order)
            # Plot interpolated data
            plot_interpolated = s_interpolated.plot(figsize=figsize, color=plot_resampled.get_lines()[-1].get_color())
            plot_interpolated.autoscale(tight=False)
            # Save plot
            plot_interpolated.get_figure().savefig(filename, dpi=80)
            # Close plot
            plt.close(plot_interpolated.get_figure())
    
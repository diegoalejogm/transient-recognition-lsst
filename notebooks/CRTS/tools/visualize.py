from . import time, io
from . import constants as k
from plotly.offline import init_notebook_mode
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
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
    outdir = k.DIR_IMAGES_SCATTERS; io.makedir(outdir)
    if io.file_exists(filename, outdir): return
    plot_df = df.plot(x='Date', y='Mag', style='.', ms=.6, figsize=(20,15))
    plot_df.autoscale(tight=False)
    plt.savefig(outdir + filename + '.png', dpi=150)
    plt.close(plot_df.get_figure())


def combined_light_curves(df_lc, n_obj, obj_type, min_obs=None, filtre=None, random_state=182):
    df_lc = df_lc.copy()
    np.random.seed(random_state)
    # Filter data
    if min_obs:
        s_grouped = df_lc.groupby(['ObjectID']).count()['ID']
        valid_obs = s_grouped[s_grouped >= min_obs].index.tolist()
        df_lc = df_lc[df_lc.ObjectID.isin(valid_obs)]
    # Sample data
    sample_obj_ids = np.random.choice(df_lc.ObjectID.unique(), n_obj, replace=False)
    df_lc_sample = df_lc[df_lc.ObjectID.isin(sample_obj_ids)].copy()

    figsize = (20,8)

    # Plot scatter of all points for every sample
    outdir = k.DIR_IMAGES_SCATTERS + '{}/'.format(obj_type)
    df_lc_sample['Day'] = ( df_lc['Date'] - datetime.datetime(2005, 4, 4) ).dt.days
    io.makedir(outdir)
    for obj_id in sample_obj_ids:
        df_obj_lc = df_lc_sample[df_lc_sample.ObjectID == obj_id]
        filename = '{}.png'.format(obj_id)
        if io.file_exists(filename, outdir): continue
        plot_df = df_obj_lc.plot.scatter(x='Day', y='Mag', yerr='Magerr', figsize=figsize, xlim=(0, 3500))
        plt.savefig(outdir + filename, dpi=110)
        plt.close(plot_df.get_figure())


    dict_plotting_data = __generate_plotting_data__(sample_obj_ids, df_lc_sample)
    # Draw LCs for each object, using all seasons
    __combined_light_curves_all_seasons__(obj_type, dict_plotting_data, figsize, local=False)
    __combined_light_curves_all_seasons__(obj_type, dict_plotting_data, figsize, local=True)
    # Draw LCs for each object type, using all seasons
    __combined_light_curves_all_seasons_by_type__(obj_type, dict_plotting_data, figsize, 3)
    # Draw LCs for each object, per season
    __combined_light_curves_per_season__(obj_type, dict_plotting_data, figsize)


def __generate_plotting_data__(sample_obj_ids, df_lc_sample):
    # Separate LCs into seasons
    for obj_id in sample_obj_ids:
        prev_MJD, season_index = None, -1
        for lc_row_index, lc_row in df_lc_sample[df_lc_sample.ObjectID == obj_id].sort_values(['MJD']).iterrows():
            current_MJD = lc_row.MJD
            if prev_MJD == None or (current_MJD - prev_MJD) >= 150:
                season_index = season_index+1
            df_lc_sample.loc[lc_row_index, 'Season'] = season_index
            prev_MJD = current_MJD
    df_lc_sample['Season'] = df_lc_sample['Season'].astype(int)

    plotting_data_dict = dict()
    seasons_list = sorted(df_lc_sample.Season.unique())
    for obj_id in sample_obj_ids:
        s_resampled_list, s_resampled_err_list, s_interpolated_list  = [], [], []
        obj_seasons_list = []
        for season_num in seasons_list:
            df_current = df_lc_sample[(df_lc_sample.ObjectID == obj_id) & (df_lc_sample.Season == season_num)]
            # Pass if current season for ObjectID is empty
            if df_current.empty: continue
            # Resample data using mean
            s_resampled = df_current.resample('D',on='Date').mean()['Mag']
            s_resampled_err = df_current.resample('D',on='Date').mean()['Magerr']
            # Interpolate data using splines
            n_rows = s_resampled[s_resampled.notnull()].shape[0]
            order = 3 if n_rows >= 5 else (2 if n_rows >= 3 else 1)
            w = (1/s_resampled[s_resampled.notnull()]).values
            s_interpolated = s_resampled.interpolate(method='spline', order=order, w=w)
#            s_interpolated = s_resampled.interpolate(method='spline', order=order)
            s_interpolated.loc[s_resampled[s_resampled.notnull()].index] = np.NaN
            s_interpolated = s_interpolated.interpolate(method='spline', order=order)
            # Add data to dict
            s_resampled_list.append(s_resampled)
            s_resampled_err_list.append(s_resampled_err)
            s_interpolated_list.append(s_interpolated)
            obj_seasons_list.append(season_num)
        obj_dict = dict()
        obj_dict['s_resampled_mag'] = s_resampled_list
        obj_dict['s_resampled_magerr'] = s_resampled_err_list
        obj_dict['s_interpolated_mag'] = s_interpolated_list
        obj_dict['seasons_list'] = obj_seasons_list
        plotting_data_dict[str(obj_id)] = obj_dict
    return plotting_data_dict


def __combined_light_curves_all_seasons__(obj_type, plotting_data, figsize, local):
    folder = 'local' if local else 'global'
    out_dir = k.DIR_IMAGES_CURVES + '{}/all-seasons/{}/'.format(str(obj_type), folder)
    io.makedir(out_dir)
    for obj_id, obj_data in plotting_data.items():
        s_resampled_list = obj_data['s_resampled_mag']
        s_resampled_err_list = obj_data['s_resampled_magerr']
        s_interpolated_list = obj_data['s_interpolated_mag']
        seasons_list = obj_data['seasons_list']
        filename = '{}.png'.format(obj_id)
        if io.file_exists(filename, out_dir, False): continue
        for i, season_num in enumerate(seasons_list):
            s_resampled = s_resampled_list[i]
            s_resampled_err = s_resampled_err_list[i]
            s_interpolated = s_interpolated_list[i]
            yerr = s_resampled_err
            # Plot known datapoints with error bars
            elw = .3 if local else .5
            plot_resampled = s_resampled.plot(figsize=figsize, yerr=yerr, fmt='.', elinewidth=elw)
            plot_resampled.autoscale(tight=False)
            # Plot interpolated data
            last_color=plot_resampled.get_lines()[-1].get_color()
            plot_interpolated = s_interpolated.plot(figsize=figsize, color=last_color)
            plot_interpolated.autoscale(tight=False)
        # Save plot
        if not local: plot_interpolated.set_ylim(8, 24)
        plot_interpolated.get_figure().savefig(out_dir + filename, dpi=110)
        # Close plot
        plt.close(plot_interpolated.get_figure())

def __combined_light_curves_all_seasons_by_type__(obj_type, plotting_data, figsize, N):
    out_dir = k.DIR_IMAGES_CURVES + '{}/all-seasons/'.format(str(obj_type))
    io.makedir(out_dir)
    filename = '{}.png'.format(obj_type)
    if io.file_exists(filename, out_dir, False): return
    for index, key in enumerate(plotting_data):
        if index == N: break
        obj_data = plotting_data[key]
        s_resampled_list = obj_data['s_resampled_mag']
        s_resampled_err_list = obj_data['s_resampled_magerr']
        s_interpolated_list = obj_data['s_interpolated_mag']
        seasons_list = obj_data['seasons_list']
        for i, season_num in enumerate(seasons_list):
            s_interpolated = s_interpolated_list[i]
            # Plot interpolated data
            last_color = None if i==0 else plot_interpolated.get_lines()[-1].get_color()
            plot_interpolated = s_interpolated.plot(figsize=figsize, color=last_color)
    # Save plot
    plot_interpolated.set_ylim(8, 24)
    plot_interpolated.get_figure().savefig(out_dir + filename, dpi=110)
    # Close plot
    plt.close(plot_interpolated.get_figure())


def __combined_light_curves_per_season__(obj_type, plotting_data, figsize):
    for obj_id, obj_data in plotting_data.items():
        # Make out dir
        out_dir = k.DIR_IMAGES_CURVES + '{}/per-season/{}/'.format(str(obj_type), obj_id)
        io.makedir(out_dir)
        s_resampled_list = obj_data['s_resampled_mag']
        s_resampled_err_list = obj_data['s_resampled_magerr']
        s_interpolated_list = obj_data['s_interpolated_mag']
        seasons_list = obj_data['seasons_list']
        for i, season_num in enumerate(seasons_list):
            filename = '{}.png'.format(i)
            if io.file_exists(filename, out_dir, False): continue
            # Get data
            s_resampled = s_resampled_list[i]
            s_resampled_err = s_resampled_err_list[i]
            s_interpolated = s_interpolated_list[i]
            # Plot known datapoints with error bars
            yerr = s_resampled_err
            plot_resampled = s_resampled.plot(figsize=figsize, yerr=yerr, fmt='.', elinewidth=.3)
            plot_resampled.autoscale(tight=False)
            # Plot interpolated data
            last_color=plot_resampled.get_lines()[-1].get_color()
            plot_interpolated = s_interpolated.plot(figsize=figsize, color=last_color)
            plot_interpolated.autoscale(tight=False)
            # Save plot
            plot_interpolated.get_figure().savefig(out_dir + filename, dpi=80)
            # Close plot
            plt.close(plot_interpolated.get_figure())

# LIBRARIES
import requests
import pandas as pd
from lxml import html
from . import constants as k
from . import io, classes
import os
import urllib.request
import numpy as np
from tools import constants
from selenium import webdriver
from astropy.table import Table
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# *** START: PUBLIC METHODS ***

# Catalogues download
def supernovae_catalog(overwrite=False):
    return __object_catalog__(classes.ObjectTypes.supernovae, overwrite)
def cv_catalog(overwrite=False):
    return __object_catalog__(classes.ObjectTypes.cv, overwrite)
def blazars_catalog(overwrite=False):
    return __object_catalog__(classes.ObjectTypes.blazars, overwrite)
def agn_catalog(overwrite=False):
    return __object_catalog__(classes.ObjectTypes.agn, overwrite)

# Light curves download
def supernovae_light_curves(df, overwrite=False):
    return __generate_light_curves__(df, classes.ObjectTypes.supernovae, overwrite)
def cv_light_curves(df, overwrite=False):
    return __generate_light_curves__(df, classes.ObjectTypes.cv, overwrite)
def blazars_light_curves(df, overwrite=False):
    return __generate_light_curves__(df, classes.ObjectTypes.blazars, overwrite)
def agn_light_curves(df, overwrite=False):
    return __generate_light_curves__(df, classes.ObjectTypes.agn, overwrite)

# *** END: PUBLIC METHODS ***

# *** START: OBJECT CATALOGUES HELPER METHODS ***
def __object_catalog__(object_type, overwrite):
    filename = '{}.pickle'.format(object_type.value)
    filepath = k.DIR_CATALOGUES_OBJECTS + filename
    file_exists = os.path.isfile(filepath)
    io.makedir(k.DIR_CATALOGUES_OBJECTS)
    if not file_exists or overwrite:
        df = pd.DataFrame()
        for url in k.OBJECTS_CATALOGUES_URLS[object_type.value]:
            df = df.append(__retrieve_object_catalog__(url))
        df.to_pickle(filepath)
    else:
        df = pd.read_pickle(filepath)
    return df
    
def __retrieve_object_catalog__(url, object_type):
    ra_list, dec_list = [], []
    date_list, clas_list = [], []
    
    r = requests.get(url)
    tree = html.fromstring(r.content)
    rows = tree.findall('.//tr')[1:]
    
    indexes = k.OBJECTS_CATALOGUES_INDEXES
    for row in rows:
        vals = row.findall('td')
        ra = vals[indexes['ra']].text_content().strip(' \t\n\r')
        dec = vals[indexes['dec']].text_content().strip(' \t\n\r')
        date = vals[indexes['date']].text_content().strip(' \t\n\r')
        clas = vals[indexes['clas']].text_content().strip(' \t\n\r')

        ra_list.append(ra); dec_list.append(dec)
        date_list.append(date); clas_list.append(clas)

    data = {'ra' : ra_list, 'dec' : dec_list, 'date' : date_list, 'clas' : clas_list}
    return pd.DataFrame(data)
# *** END: OBJECT CATALOGUES HELPER METHODS ***

#  *** START: LIGHT CURVES HELPER METHODS ***
def __init_driver__():
    driver = webdriver.PhantomJS()
    driver.set_window_size(800, 600)  
    return driver
        
def __light_curve_url__(ra, dec, db, driver):
    driver.find_element_by_css_selector('input[name="RA"]').send_keys(str(ra))
    driver.find_element_by_css_selector('input[name="Dec"]').send_keys(str(dec))
    driver.find_element_by_css_selector('input[value="{}"]'.format(db)).click()
    driver.find_element_by_css_selector('input[name=".submit"]').click()
    try:
        element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'font[color="red"], input[value="view"]')
            ))
        view_button = driver.find_element_by_css_selector('input[value="view"]')
        url = view_button.get_attribute('onclick').split('=')[1][1:-1]
        return url
    except Exception as e:
        return None

def __retrieve_light_curve__(ra, dec, driver, filename, out_dir):
    url = 'http://nunuku.caltech.edu/cgi-bin/getcssconedb_release_img.cgi'
    driver.get(url)
    lc_url = __light_curve_url__(ra, dec, 'photcat', driver)
    if not lc_url:
        driver.get(url)
        lc_url = __light_curve_url__(ra, dec, 'orphancat', driver)
    if lc_url:
        lc_path = __download_file__(lc_url, filename, out_dir)
        return lc_path
    else:
        print('No light curve found for', ra, dec)
        return None
    
def __consolidate_light_curves__(obj_cat_df, object_type, overwrite=False):
    outdir = k.DIR_CATALOGUES_LIGHTCURVES_GROUPED
    filename = object_type.value
    io.makedir(outdir)
    filepath = outdir + filename
    if not io.file_exists(filename, outdir) or overwrite:
        consolidated_df = pd.DataFrame()
        for i, obj in obj_cat_df.iterrows():
            lightcurve_df = Table.read(obj['light_curve_path'], format='ascii').to_pandas()
            consolidated_df = consolidated_df.append(lightcurve_df, ignore_index=True)
        consolidated_df.to_pickle(filepath)
        return consolidated_df
    else:
        return pd.read_pickle(filepath)
    
def __generate_light_curves__(obj_catalog_df, object_type, overwrite):
    driver = __init_driver__()
    if not 'light_curve_path' in obj_catalog_df.columns:
        obj_catalog_df['light_curve_path'] = np.nan
    for index, row in obj_catalog_df.iterrows():
        ra, dec = row['ra'], row['dec']
        filename = '{}-{}.tbl'.format(ra,dec)
        out_dir = k.DIR_CATALOGUES_LIGHTCURVES_SINGLE
        filepath = out_dir + filename
        file_exists = os.path.isfile(filepath)
        if not file_exists or overwrite:
            light_curve_path = __retrieve_light_curve__(ra, dec, driver, filename, out_dir)
            obj_catalog_df.loc[index, 'light_curve_path'] = light_curve_path
        else:
            obj_catalog_df.loc[index, 'light_curve_path'] = filepath
    driver.quit()
    
    # Consolidate Light Curves
    light_curves_df = __consolidate_light_curves__(obj_catalog_df, object_type, overwrite=overwrite)
    return light_curves_df
#  *** END: LIGHT CURVES HELPER METHODS ***

def __download_file__(url, name, outdir, overwrite=False):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    filepath = outdir + name
    file_exists = os.path.isfile(filepath)
    if file_exists and not overwrite:
        print('File {} already exists'.format(name))
        pass
    else:        
        print('Downloading {}'.format(filepath))
        urllib.request.urlretrieve(url, filepath)
    return filepath
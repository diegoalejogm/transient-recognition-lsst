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
from selenium.common.exceptions import TimeoutException
import time

# *** START: PUBLIC METHODS ***

# Catalogues download
def all_transients_catalog(overwrite=False):
    outdir = k.DIR_CATALOGUES_OBJECTS
    io.makedir(outdir)
    filename = 'all_transients.pickle'
    filepath = outdir + filename
    file_exists = os.path.isfile(filepath)
    if file_exists and not overwrite:
        all_transients_catalog = pd.read_pickle(filepath)
        return all_transients_catalog
    else:
        all_transients_catalog = pd.DataFrame()
        for transient_type in classes.ObjectTypes:
            new_catalog = __transient_catalog__(transient_type, overwrite)
            new_catalog['type'] = transient_type.value.upper()
            all_transients_catalog = all_transients_catalog.append(new_catalog, ignore_index=True)
        all_transients_catalog.reset_index(drop=True, inplace=True)
        all_transients_catalog.to_pickle(filepath)
        return all_transients_catalog

# Catalogues download
def all_permanents_catalog(permanents_light_curves_df, overwrite=False):
    outdir = k.DIR_CATALOGUES_OBJECTS
    io.makedir(outdir)
    filename = 'all_permanents.pickle'
    filepath = outdir + filename
    file_exists = os.path.isfile(filepath)
    if file_exists and not overwrite:
        all_permanents_catalog = pd.read_pickle(filepath)
        return all_permanents_catalog
    else:
        all_permanents_catalog = permanents_light_curves_df[['ID','RA','Decl','ObjID']].groupby('ID').mean()
        all_permanents_catalog.rename(columns={'RA':'ra', 'Decl':'dec'}, inplace=True)
        all_permanents_catalog['type'] = 'PERMANENT'
        all_permanents_catalog.set_index(['ObjID'], drop=True, inplace=True)
        all_permanents_catalog.sort_index(inplace=True)
        all_permanents_catalog.to_pickle(filepath)
        return all_permanents_catalog

# Light curves download
def all_transients_light_curves(df, overwrite=False):
    all_transients_light_curves = __generate_light_curves__(df, overwrite=overwrite, ispermanent=False)
    return all_transients_light_curves

def all_permanents_light_curves(transient_catalog_df, transient_light_curves_df, overwrite=False):
    all_permanents_light_curves = __generate_light_curves__(
        obj_catalog_df=transient_catalog_df,
        ispermanent=True,
        overwrite=overwrite,
        transient_IDs=transient_light_curves_df.ID.astype(str)
    )
    return all_permanents_light_curves

# *** END: PUBLIC METHODS ***

# *** START: OBJECT CATALOGUES HELPER METHODS ***
def __transient_catalog__(object_type, overwrite):
    filename = '{}.pickle'.format(object_type.value)
    filepath = k.DIR_CATALOGUES_OBJECTS + filename
    file_exists = os.path.isfile(filepath)
    io.makedir(k.DIR_CATALOGUES_OBJECTS)
    if not file_exists or overwrite:
        df = pd.DataFrame()
        for url in k.OBJECTS_CATALOGUES_URLS[object_type.value]:
            df = df.append(__retrieve_object_catalog__(url, object_type))
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

    indexes = k.OBJECTS_CATALOGUES_INDEXES[object_type.value]
    for row in rows:
        vals = row.findall('td')
        if len(vals) < 4:
            continue
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
    driver = webdriver.Chrome()
    driver.set_window_size(700, 1800)
    driver.set_page_load_timeout(600)
    return driver

def __raw_light_curves_url__(query_file_path, driver, use_orphancat=True):
    query_file_path = os.path.abspath(query_file_path)
    if use_orphancat:
        driver.find_element_by_css_selector('input[name="DB"][value="orphancat"]').click()
    driver.find_element_by_css_selector('input[name="upload_file"]').send_keys(query_file_path)
    driver.find_element_by_css_selector('input[type="submit"]').send_keys("\n")
    submit_button = driver.find_elements(By.XPATH, '//input[@type="submit"]')
    if len(submit_button):
        submit_button[0].click()
        txtCaptchaDiv = driver.find_element_by_css_selector('span[id="txtCaptchaDiv"]')
        txtInput = driver.find_element_by_css_selector('input[name="txtInput"]')
        print('Captcha Text', txtCaptchaDiv.text)
        txtInput.send_keys(txtCaptchaDiv.text)
        driver.find_element_by_css_selector('button[type="submit"]').click()
    view_button = driver.find_element_by_css_selector('input[type="button"]')
    url = view_button.get_attribute('onclick').split('=')[1][1:-1]
    return url

def __retrieve_light_curves__(query_file_path, filename, outdir, use_orphancat=True):
    done = False
    file_url = None
    url = 'http://nesssi.cacr.caltech.edu/cgi-bin/getmulticonedb_release2.cgi'
    driver = __init_driver__()
    while not done:
        try:
            driver.get(url)
            file_url = __raw_light_curves_url__(query_file_path, driver, use_orphancat)
            driver.quit()
            done = True
        except TimeoutException as e:
            print('Timeout Exception. Will try again.')
    if file_url:
        raw_light_curves_path = __download_file__(file_url, filename, outdir, overwrite=True)
        return raw_light_curves_path
    else:
        return None

def __create_query_file__(obj_catalog_df, ispermanent, start_index, end_index):
    query_file_path = './query_file.txt'
    with open(query_file_path, 'w+') as file:
        for i, row in obj_catalog_df[start_index:end_index].iterrows():
            index = i
            ra = row['ra']
            dec = row['dec']
            rad = 0.006 if ispermanent else 0.002
            file.write('{} {} {} {}\n'.format(i, ra, dec, rad))
    return query_file_path

def __format_raw_light_curves__(raw_light_curves_df, ispermanent=None, transient_IDs=None):
    if ispermanent:
        raw_light_curves_df['ID'] = raw_light_curves_df['ID'].astype(str)
        query = raw_light_curves_df['ID'].isin(transient_IDs.unique())
        raw_light_curves_df.drop(raw_light_curves_df[query].index, inplace=True)
        print('Num Objects: {}'.format(len(raw_light_curves_df.ID.unique())))
    else:
        raw_light_curves_df.rename(columns={'InputID':'ObjectID'}, inplace=True)

def __consolidate_light_curves_df__(obj_catalog_df, ispermanent, transient_IDs=None):
    outdir = k.DIR_CATALOGUES_LIGHTCURVES_GROUPED_TEMP_OBJECTS if ispermanent else k.DIR_CATALOGUES_LIGHTCURVES_GROUPED_TEMP_TRANSIENTS
    io.makedir(outdir)
    light_curves_df = pd.DataFrame()
    step, n_rows = 50 if ispermanent else 100, obj_catalog_df.shape[0]
    for i in range(0, 49, step):
        temp_light_curves_filename = 'part{}.tbl'.format(int(i/step))
        light_curves_table_path = outdir + temp_light_curves_filename
        if not io.file_exists(temp_light_curves_filename, outdir, verbose=False):
            query_file_path = __create_query_file__(obj_catalog_df, ispermanent, start_index=i, end_index=i+step)
            light_curves_table_path = __retrieve_light_curves__(query_file_path, temp_light_curves_filename, outdir, use_orphancat=(not ispermanent))
            if not light_curves_table_path: print('Error in seq. {}, curves not found'.format(i)); continue;
        temp_light_curves_df = Table.read(light_curves_table_path, format='ascii').to_pandas()
        __format_raw_light_curves__(temp_light_curves_df, ispermanent, transient_IDs)
        light_curves_df = light_curves_df.append(temp_light_curves_df, ignore_index=True)
    light_curves_df.drop_duplicates(keep='first', inplace=True)
    if ispermanent:
        # Add ObjId column
        for i, index in enumerate(light_curves_df.ID.unique()):
            light_curves_df.loc[light_curves_df.ID == index, 'ObjID'] = i
        light_curves_df['ObjID'] = light_curves_df['ObjID'].astype(int)
    return light_curves_df

def __generate_light_curves__(obj_catalog_df, overwrite, ispermanent, transient_IDs=None):
    outdir = k.DIR_CATALOGUES_LIGHTCURVES_GROUPED
    io.makedir(outdir)
    filename = 'all_permanents_light_curves.pickle' if ispermanent else 'all_transients_light_curves.pickle'
    filepath = outdir + filename
    if io.file_exists(filename, outdir) and not overwrite:
        return pd.read_pickle(filepath)
    else:
        light_curves_df = __consolidate_light_curves_df__(obj_catalog_df, ispermanent, transient_IDs)
        light_curves_df.to_pickle(filepath)
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

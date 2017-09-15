# LIBRARIES
import pandas as pd
import urllib.request
from urllib.parse import urlencode
import os
from . import constants

# HELPER METHOD TO OBTAIN OBJECT CATALOGUES URL REQUEST
def __object_cat_url__(outrows, transient):
    query = dict()
    query['catalog'] = 'ptf_objects'
    query['spatial'] = 'None'
    query['selcols'] = 'ra,dec,oid,nobs,ngoodobs'
    query['outfmt'] = '1'
    query['outrows'] = '{}'.format(outrows)
    query['constraints'] = 'nobs >= 20 AND ngoodobs>= 15' + (' AND transient_flag=1' if  transient else '')
    query_url = constants.CATALOG_API + '?' + urlencode(query)
    return query_url

def transient_cat(outrows, overwrite=False):
    query_url = __object_cat_url__(outrows, transient=True)
    output_directory = constants.DIR_CATALOGUES_OBJECTS
    filename = 'transient_cat.tbl'
    file_path = __download_file__(query_url, filename, output_directory, overwrite)
    return file_path

def permanent_cat(outrows, overwrite=False):
    query_url = __object_cat_url__(outrows, transient=False)
    output_directory = constants.DIR_CATALOGUES_OBJECTS
    filename = 'permanent_cat.tbl'
    file_path = __download_file__(query_url, filename, output_directory, overwrite)
    return file_path

# HELPER METHOD TO OBTAIN LIGHT-CURVES URL REQUEST
def __light_url__(ra, dec):
    query = dict()
    query['catalog'] = 'ptf_lightcurves'
    query['spatial'] = 'None'
    query['selcols'] = 'oid,ra,dec,obsmjd,mag_autocorr,goodflag'
    query['outfmt'] = '1'
    query['constraints'] = 'ra={} AND dec={} AND fid=2'.format(ra, dec)
    query['order'] = 'obsmjd'
    
    query_url = constants.CATALOG_API + '?' + urlencode(query)
    return query_url

def light_curves(obj_cat_df, transient, overwrite=False, limit=None, append_series=False):
    output_directory = constants.DIR_LIGHTCURVES_RED + ('transient' if transient else 'permanent')
    file_paths = []
    for i, row in obj_cat_df.iterrows():
        if limit and i == limit:
            break
        else:
            objid = row['oid']
            query_url = __light_url__(row['ra'], row['dec'])
            file_path = __download_file__(query_url, '{}.tbl'.format(objid), output_directory, overwrite)
            file_paths.append(file_path)
    resp = pd.Series(file_paths)
    if append_series:
        obj_cat_df['lightcurve_path'] = resp
    return resp

# HELPER METHOD TO DOWNLOAD FILES
def __download_file__(url, name, outdir, overwrite=False):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    filepath = outdir + '/' + name
    file_exists = os.path.isfile(filepath)
    if file_exists and not overwrite:
        print('File {} already exists'.format(name))
        pass
    else:        
        print('Downloading {}'.format(filepath))
        urllib.request.urlretrieve(url, filepath)
    return filepath
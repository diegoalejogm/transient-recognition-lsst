# REQUIRES ADDING 'lighcurve_path' COL TO INPUT DF
def lightcurve_real_nobs(obj_cat_df, limit):
    real_nobs = []
    for i, obj in obj_cat_df.iterrows():
        if limit and i == limit:
            break
        else:
            lightcurve_df = Table.read(obj_cat_df['lightcurve_path'], format='ascii').to_pandas()
            real_nobs.append(lightcurve_df.shape[0])
    return real_nobs
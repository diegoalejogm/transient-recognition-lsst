from . import classes

DIR_DATA = '../../data/CRTS/'
DIR_CATALOGUES = DIR_DATA + 'catalogues/'
DIR_CATALOGUES_OBJECTS = DIR_CATALOGUES + 'objects/'
DIR_CATALOGUES_LIGHTCURVES = DIR_CATALOGUES + 'lightcurves/'
DIR_CATALOGUES_LIGHTCURVES_SINGLE = DIR_CATALOGUES_LIGHTCURVES + 'single/'
DIR_CATALOGUES_LIGHTCURVES_GROUPED = DIR_CATALOGUES_LIGHTCURVES + 'grouped/'
## SUPERNOVAE CATALOGUES
SUPERNOVAE_CSS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/catalina/AllSN.arch.html'
SUPERNOVAE_MLS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/MLS/AllSN.arch.html'
SUPERNOVAE_SSS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/SSS/AllSN.html'
SUPERNOVAE_CATALOGUES_URLS = [SUPERNOVAE_CSS_CATALOG_URL, SUPERNOVAE_MLS_CATALOG_URL, SUPERNOVAE_SSS_CATALOG_URL]

## CATACLYSMIC VARIABLES CATALOGUES
CV_CSS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/catalina/AllCV.arch.html'
CV_MLS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/MLS/AllCV.arch.html'
CV_SSS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/SSS/AllCV.html'
CV_CATALOGUES_URLS = [CV_CSS_CATALOG_URL, CV_MLS_CATALOG_URL, CV_SSS_CATALOG_URL]

## BLAZARS CATALOGUES
BLAZARS_CSS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/catalina/AllBlaz.arch.html'
BLAZARS_MLS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/MLS/AllBlaz.arch.html'
BLAZARS_SSS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/SSS/AllBlaz.html'
BLAZARS_CATALOGUES_URLS = [BLAZARS_CSS_CATALOG_URL, BLAZARS_MLS_CATALOG_URL, BLAZARS_SSS_CATALOG_URL]

## AGN CATALOGUES
AGN_CSS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/catalina/AllAGN.arch.html'
AGN_MLS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/MLS/AllAGN.arch.html'
AGN_SSS_CATALOG_URL = 'http://nesssi.cacr.caltech.edu/SSS/AllAGN.html'
AGN_CATALOGUES_URLS = [AGN_CSS_CATALOG_URL, AGN_MLS_CATALOG_URL, AGN_SSS_CATALOG_URL]

OBJECTS_CATALOGUES_URLS = {
    classes.ObjectTypes.supernovae.value : SUPERNOVAE_CATALOGUES_URLS,
    classes.ObjectTypes.cv.value : CV_CATALOGUES_URLS,
    classes.ObjectTypes.blazars.value : BLAZARS_CATALOGUES_URLS,
    classes.ObjectTypes.agn.value : AGN_CATALOGUES_URLS
}

OBJECTS_CATALOGUES_INDEXES = {
    classes.ObjectTypes.supernovae.value : {'ra':1, 'dec':2, 'date':5, 'clas':13},
    classes.ObjectTypes.cv.value : {'ra':1, 'dec':2, 'date':5, 'clas':12},
    classes.ObjectTypes.blazars.value : {'ra':1, 'dec':2, 'date':4, 'clas':12},
    classes.ObjectTypes.agn.value : {'ra':1, 'dec':2, 'date':4, 'clas':12}
}
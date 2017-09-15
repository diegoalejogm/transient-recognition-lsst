import os

def makedir(outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
def file_exists(filename, outdir, verbose=True):
    filepath = outdir + '/' + filename
    file_exists = os.path.isfile(filepath)
    if file_exists and verbose:
        print('File {} already exists'.format(filename))
    return file_exists
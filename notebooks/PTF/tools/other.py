import pandas as pd
import math, timeit, sys, os
import urllib.request

def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize: # near the end
            sys.stderr.write("\n")
    else: # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))

def download_file(url, name, outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    filepath = outdir + '/' + name
    urllib.request.urlretrieve(url, filepath, reporthook)
    return filepath

def table_to_dataframe(path):
    start = timeit.default_timer()

    with open(path) as file:
        lines = file.readlines()
    lines = [l.strip() for l in lines]
    num_lines = len(lines)
    # Print total num. of lines in file
    print(num_lines)

    # Process keywords & comments
    index = 0
    while len(lines[index]) ==0 or lines[index][0] == '\\': index += 1

    # Process Column names
    col_names = lines[index].split('|')
    col_names = [col.strip() for col in col_names[1:-1]]
    index += 1

    # Process Data types, units & nulls
    while lines[index][0] == '|': index = index+1

    # Process Rows
    num_rows = num_lines - index
    curr_row_num = 1
    ten_percent_num_rows = math.floor(num_rows / 10)
    data = {col_name:[] for col_name in col_names}
    while index < len(lines):

        # Clean
        row = lines[index].split(' ')
        row = [value.strip() for value in row]
        # Store
        j = 0
        for value in row:
            if len(value) == 0: continue
            col_name = col_names[j]
            data[col_name].append(value)
            j += 1
        index += 1

    df = pd.DataFrame(data=data)
    stop = timeit.default_timer()
    print('TOTAL TIME', stop - start)
    return df

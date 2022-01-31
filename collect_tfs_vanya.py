import sys
import os
import pandas as pd
from zipfile import ZipFile

int_tfs = ['Q01094', 'P25490']
models = ['macs2']
master_list_path = sys.argv[1]
master_list = pd.read_csv(master_list_path,
                          header=None,
                          names=['Specie', 'TF', 'Name', 'Caller', 'Select', 'Type', 'Max', 'Min'])
master_list = master_list[master_list['TF'].in_(int_tfs)]
master_list = master_list[master_list['Caller'].in_(models)]
archive_path = sys.argv[2]
out_path = sys.argv[3]
if not os.path.exists(out_path):
    os.mkdir(out_path)
for tf in int_tfs:
    tf_path = os.path.join(out_path, tf)
    if not os.path.exists(tf_path):
        os.mkdir(tf_path)
    peaks = master_list['Name']
    peaks = set(peaks[peaks == tf].tolist())
    with ZipFile(archive_path, 'r') as zipObj:
        # Get a list of all archived file names from the zip
        list_of_file_names = zipObj.namelist()
        # Iterate over the file names
        for file_name in list_of_file_names:
            # Check filename endswith csv
            _, name, caller, _ = file_name.split('/')
            if name in peaks and caller in models:
                # Extract a single file from zip
                zipObj.extract(file_name, tf_path)

import sys
import os
import pandas as pd
import shutil

mouse_dir = os.path.expanduser('~/mouse')
if len(sys.argv) > 1:
    meta_path = sys.argv[1]
else:
    raise AssertionError('No meta file provided!')
master_df = pd.read_table(meta_path, header=None, names=['TF_ID', 'PEAKS'])
for peak_type in os.listdir(os.path.expanduser('~/grouped_peaks')):
    os.mkdir(os.path.join(mouse_dir, peak_type))
for index, row in master_df.iterrows():
    for peak_type in os.listdir(os.path.expanduser('~/grouped_peaks')):
        base_path = os.path.join(os.path.expanduser('~/grouped_peaks'), peak_type, row['PEAKS'] + '.interval')
        if os.path.exists(base_path):
            shutil.copy2(base_path, os.path.join(mouse_dir, peak_type, row['PEAKS'] + '.interval'))

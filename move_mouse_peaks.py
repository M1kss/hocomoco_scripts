import sys
import os
import pandas as pd
import shutil
from tqdm import tqdm

mouse_dir = os.path.expanduser('~/mouse')
if len(sys.argv) > 1:
    meta_path = sys.argv[1]
else:
    raise AssertionError('No meta file provided!')
master_df = pd.read_table(meta_path, header=None, names=['TF_ID', 'PEAKS'])
for peak_type in os.listdir(os.path.expanduser('~/grouped-peaks')):
    new_dir = os.path.join(mouse_dir, peak_type)
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
for index, row in tqdm(master_df.iterrows(), total=len(master_df.index)):
    base_path = os.path.join(os.path.expanduser('~/hocomoco-peaks'), row['PEAKS'])
    if os.path.exists(base_path):
        for peak_type in os.listdir(base_path):
            new_dir = os.path.join(mouse_dir, peak_type)
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
            shutil.copy2(os.path.join(base_path, peak_type, row['PEAKS'] + '.interval'), os.path.join(mouse_dir, peak_type, row['PEAKS'] + '.interval'))

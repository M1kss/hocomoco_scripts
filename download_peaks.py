import os
import subprocess
import pandas as pd
from tqdm import tqdm

df = pd.read_table('~/mouse/mouse_peaks_dn.tsv')
df = df[~df['DOWNLOAD_PATH'].isna() & (df['DOWNLOAD_PATH'] != 'None')]
for index, row in tqdm(df.iterrows()):
    print(['scp', '-P', '1300', '-T',
                     'autosome@localhost:' + row['DOWNLOAD_PATH'],
                      '~/mouse/peaks/'])
    subprocess.Popen(['scp', '-P', '1300', '-T',
                     'autosome@localhost:' + row['DOWNLOAD_PATH'],
                      '~/mouse/peaks/'])

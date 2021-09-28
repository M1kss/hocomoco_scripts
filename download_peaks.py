import os
import subprocess
import pandas as pd
from tqdm import tqdm

df = pd.read_table('~/mouse/mouse_peaks_dn.tsv')
df = df[~df['DOWNLOAD_PATH'].isna()]
for index, row in tqdm(df.iterrows()):
    subprocess.Popen(['scp', '-P', '1300', '-T',
                      ' '.join([x + 'autosome@localhost:~/' for x in row['DOWNLOAD_PATH'].split()]),
                      '~/mouse/peaks/'])

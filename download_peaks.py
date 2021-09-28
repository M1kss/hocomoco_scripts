import os.path
import time
import subprocess
import pandas as pd
from tqdm import tqdm

df = pd.read_table('~/mouse/mouse_peaks_dn.tsv')
df = df[~df['DOWNLOAD_PATH'].isna() & (df['DOWNLOAD_PATH'] != 'None')]
for index, row in tqdm(df.iterrows(), total=len(df.index)):
    time.sleep(0.01)
    for peak_path in row['DOWNLOAD_PATH'].split():
        peak_type = os.path.dirname(peak_path)
        print(peak_type)
        # process = subprocess.Popen(['scp', '-T', '-P', '1300',
        #                  'autosome@localhost:' + peak_path,
        #                   '~/mouse/peaks/'])
        # process.wait()

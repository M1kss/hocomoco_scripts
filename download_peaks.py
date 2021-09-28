import os.path
import time
import subprocess
import pandas as pd
from tqdm import tqdm

out_path = os.path.expanduser('~/mouse/peaks')
df = pd.read_table('~/mouse/mouse_peaks_dn.tsv')
df = df[~df['DOWNLOAD_PATH'].isna() & (df['DOWNLOAD_PATH'] != 'None')]
with open('scp.log', 'w') as f:
    for index, row in tqdm(df.iterrows(), total=len(df.index)):
        for peak_path in row['DOWNLOAD_PATH'].split():
            peak_type = os.path.basename(os.path.dirname(peak_path))
            dir_path = os.path.join(out_path, peak_type)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            process = subprocess.Popen(['scp', '-P', '1300',
                                        'autosome@localhost:' + peak_path,
                                        dir_path], stdout=f)
            process.wait()

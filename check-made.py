import sys
import os
import pandas as pd

df = pd.read_csv(sys.argv[1], header=None, names=['specie', 'tf', 'exp', 'type', 'ps', 'fs', 'maxl', 'minl'])
df['path'] = df.apply(lambda x: os.path.join(sys.argv[2], '.'.join([x['exp'], x['type'], x['ps'], x['fs']]) + '.out'), axis=1)
df = df[df['path'].apply(lambda x: not os.path.isfile(x))]
print(df)
df.to_csv(sys.argv[3], index=False, header=False)
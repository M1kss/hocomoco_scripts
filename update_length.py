import sys

import pandas as pd
import os

from cor import read_xlsx_master

specie = 'Mus Musculus'


def get_len(row, len_d, mode):
    return len_d[row['TF_ID']][mode]


def get_extended_rows(row, callers_dict):
    rows = []
    for caller in callers_dict.get(row['PEAKS'], ()):
        for rank_type in ['score'] + (['pvalue'] if caller != 'cpics' else []):
            for motif_type in ['flat', 'single']:
                new_row = row.to_dict()
                new_row['RANK_TYPE'] = rank_type
                new_row['MOTIF_TYPE'] = motif_type
                new_row['CALLER'] = caller
                rows.append(new_row)
    return rows


def make_length_dict(ann_df):
    d = {}
    for index, row in ann_df.iterrows():
        d[row['curated:uniprot_ac']] = {
            'min': row['min_motif_len'],
            'max': row['max_motif_len'],
        }
    return d


def main(master_path, out_path):
    common_header = ['Specie', 'TF_ID', 'Peaks',
                     'Caller', 'Select_by', 'Type']
    df = read_xlsx_master()
    convert_d = df.set_index('curated:uniprot_ac')['curated:uniprot_id'].to_dict()
    print(convert_d)
    master = pd.read_csv(master_path, header=None,
                           names=[*common_header, 'Max_len', 'Min_len'])
    print(len(master.index))
    master = master[master['TF_ID'].apply(lambda x: x in convert_d and convert_d[x] == 'CTCF_MOUSE')]
    print(len(master.index))
    master['TF_NAME'] = master['TF_ID'].apply(lambda x: convert_d[x])
    ann_df = pd.read_table(os.path.join('files', 'len_annotated.tsv'))
    len_d = make_length_dict(ann_df)
    master['MIN_LEN'] = master.apply(lambda x: get_len(x, len_d, 'min'), axis=1)
    master['MAX_LEN'] = master.apply(lambda x: get_len(x, len_d, 'max'), axis=1)
    master[['Specie', 'TF_NAME', 'Peaks',
            'Caller', 'Select_by', 'Type',
            'MAX_LEN', 'MIN_LEN']].to_csv(out_path,
                                          sep=',', header=None, index=False)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise AssertionError('No meta file provided!')
    main(sys.argv[1], sys.argv[2])

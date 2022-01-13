import sys

import pandas as pd
import os

from cor import read_xlsx_master

specie = 'Mus Musculus'


def get_len(row, ann_df, mode):
    try:
        filtered_df = ann_df[
            ann_df['curated:uniprot_ac'] == row['TF_ID']][
            '{}_motif_len'.format(mode)
        ].reset_index(drop=True)
        if len(filtered_df.index) == 0:
            raise AssertionError
        return filtered_df[0]
    except AssertionError:
        if mode == 'max':
            return 24
        elif mode == 'min':
            return 7
        else:
            raise AssertionError('Mode {} not in "max" or "min"'.format(mode))


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


def main(master_path, out_path):
    common_header = ['Specie', 'TF_ID', 'Peaks',
                     'Caller', 'Select_by', 'Type']
    df = read_xlsx_master()
    convert_d = df.set_index('curated:uniprot_ac')['curated:uniprot_id'].to_dict()
    master = pd.read_csv(master_path, header=None,
                           names=[*common_header, 'Max_len', 'Min_len'])
    master = master[master['TF_ID'].apply(lambda x: x in convert_d)]
    master['TF_NAME'] = master['TF_ID'].apply(lambda x: convert_d[x] and convert_d[x] == 'CTCF_MOUSE')
    ann_df = pd.read_table(os.path.join('files', 'len_annotated.tsv'))
    master['MIN_LEN'] = master.apply(lambda x: get_len(x,
                                                       mode='min',
                                                       ann_df=ann_df), axis=1)
    master['MAX_LEN'] = master.apply(lambda x: get_len(x,
                                                       mode='max',
                                                       ann_df=ann_df), axis=1)
    print(master)
    master[['Specie', 'TF_NAME', 'Peaks',
            'Caller', 'Select_by', 'Type',
            'MAX_LEN', 'MIN_LEN']].to_csv(out_path,
                                          sep='\t', header=None)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise AssertionError('No meta file provided!')
    main(sys.argv[1], sys.argv[2])

import json
import sys

import pandas as pd
import os
from get_length import main as craft_motif_length_file

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


def main(master_path):
    with open(os.path.join('source_files', 'callers.json')) as out:
        callers_dict = json.load(out)
    master = pd.read_table(master_path, header=None, names=['TF_ID', 'PEAKS'])
    ann_df = pd.read_table(os.path.join('files', 'len_annotated.tsv'))
    master['SPECIE'] = specie
    master['MIN_LEN'] = master.apply(lambda x: get_len(x,
                                                       mode='min',
                                                       ann_df=ann_df), axis=1)
    master['MAX_LEN'] = master.apply(lambda x: get_len(x,
                                                       mode='max',
                                                       ann_df=ann_df), axis=1)

    dfs = []
    for index, row in master.iterrows():
        dfs.append(pd.DataFrame(get_extended_rows(row, callers_dict)))
    extended_master = pd.concat(dfs)

    extended_master[['SPECIE', 'TF_ID', 'PEAKS', 'CALLER', 'RANK_TYPE', 'MOTIF_TYPE', 'MAX_LEN', 'MIN_LEN']].to_csv(
        'master_peaks.csv',
        sep=',',
        index=False,
        header=False)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        meta_path = sys.argv[1]
    else:
        raise AssertionError('No meta file provided!')
    craft_motif_length_file()
    main(meta_path)

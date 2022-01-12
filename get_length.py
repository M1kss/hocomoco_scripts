import numpy as np
import pandas as pd
import os
from tqdm import tqdm

from cor import dict_types, read_dicts, check_dir_for_collection


def get_motif_length_from_list(len_list, mode):
    if len(len_list) == 0:
        if mode == 'max':
            return 24
        if mode == 'min':
            return 7
    elif len(len_list) < 4:
        if mode == 'max':
            return np.max(len_list) + 1
        if mode == 'min':
            return max(np.min(len_list) - 1, 7)
    else:
        upper_quartile = np.percentile(len_list, 75)
        lower_quartile = np.percentile(len_list, 25)
        IQR = (upper_quartile - lower_quartile) * 1.5
        valid_list = [x for x in len_list if lower_quartile - IQR <= x <= upper_quartile + IQR]
        if mode == 'max':
            return max(valid_list) + 1
        if mode == 'min':
            return max(min(valid_list) - 1, 7)


def main():
    max_len_list = []
    min_len_list = []
    counter = 0
    master_df = pd.read_excel(os.path.join('source_files', 'hocomoco_2021.xlsx'))
    dicts = read_dicts()
    for index, row in tqdm(master_df.iterrows()):
        tf_name = row['curated:uniprot_id']
        to_skip = False
        tf_len_list = None
        for d_type in dict_types:
            if not to_skip:
                tf_motifs = dicts[d_type].get(tf_name)
                if tf_motifs:
                    tf_len_list = [len(pd.read_table(x, comment='#').index) for x in
                                   check_dir_for_collection(tf_name,
                                                            tf_motifs.get(tf_name),
                                                            d_type, False)
                                   ]
                    to_skip = True
        if not tf_len_list:
            tf_len_list = []
        max_len_list.append(get_motif_length_from_list(
            tf_len_list, 'max')
        )
        min_len_list.append(get_motif_length_from_list(
            tf_len_list, 'min')
        )
    master_df['max_motif_len'] = max_len_list
    master_df['min_motif_len'] = min_len_list
    master_df.to_csv(os.path.join('files', 'len_annotated.tsv'),
                     index=False,
                     sep='\t')
    # print(counter)


if __name__ == '__main__':
    main()

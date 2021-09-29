import numpy as np
import pandas as pd
import os
from tqdm import tqdm


def get_motif_length(len_list, mode):
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


def parse_hoco(peaks_df):
    # di_pwm_path = os.path.expanduser('~/Desktop/dipwms')

    # for path in os.listdir(di_pwm_path):
    #     if not path.endswith('.A.dpwm') or path.endswith('.B.dpwm'):
    #         continue
    #     tf_name = path.split('.')[0]
    #     len_pwm = len(pd.read_table(os.path.join(di_pwm_path, path), header=None, comment='>').index) + 1
    #     p_df = peaks_df[peaks_df['NAME'] == tf_name]
    #     subfamily = str(p_df['subfamily'].reset_index(drop=True)[0]) if not p_df['subfamily'].empty else None
    #     family = str(p_df['family'].reset_index(drop=True)[0]) if not p_df['family'].empty else None
    #     try:
    #         tfs_dict['TFs'][tf_name].append(len_pwm)
    #     except KeyError:
    #         tfs_dict['TFs'][tf_name] = [len_pwm]
    #     try:
    #         tfs_dict['family'][family].append(len_pwm)
    #     except KeyError:
    #         tfs_dict['family'][family] = [len_pwm]
    #     try:
    #         tfs_dict['subfamily'][subfamily].append(len_pwm)
    #     except KeyError:
    #         tfs_dict['subfamily'][subfamily] = [len_pwm]
    tfs_dict = {'TFs': {}, 'family': {}, 'subfamily': {}}
    pwm_path = 'hocomoco_pwms'
    for path in os.listdir(pwm_path):
        if not path.endswith('.A.pwm') or path.endswith('.B.pwm'):
            continue
        tf_name = path.split('.')[0]
        len_pwm = len(pd.read_table(os.path.join(pwm_path, path), header=None, comment='>').index)
        p_df = peaks_df[peaks_df['NAME'] == tf_name]
        subfamily = str(p_df['subfamily'].reset_index(drop=True)[0]) if not p_df['subfamily'].empty else None
        family = str(p_df['family'].reset_index(drop=True)[0]) if not p_df['family'].empty else None
        try:
            tfs_dict['TFs'][tf_name].append(len_pwm)
        except KeyError:
            tfs_dict['TFs'][tf_name] = [len_pwm]
        try:
            tfs_dict['family'][family].append(len_pwm)
        except KeyError:
            tfs_dict['family'][family] = [len_pwm]
        try:
            tfs_dict['subfamily'][subfamily].append(len_pwm)
        except KeyError:
            tfs_dict['subfamily'][subfamily] = [len_pwm]
    return tfs_dict


def parse_annotation():
    result = {}
    ann_df = pd.read_table(
        os.path.join('source_files', 'annotation_2.txt'), header=None)
    ann_df = ann_df[[0, 26, 27]]
    ann_df.columns = ['id', 'family', 'subfamily']
    for index, row in ann_df.iterrows():
        for name in ['subfamily', 'family']:
            if row[name] == '__na':
                row[name] = None
        result[row['id']] = row[['subfamily', 'family']].to_dict()
    print(result)
    return result


def add_meta(row, annotation_dict):
    k = annotation_dict.get(row['#ID'])
    if k is not None:
        sf, f = k
    else:
        sf, f = None, None
    row['subfamily'] = sf
    row['family'] = f
    return row


def main():
    max_len_list = []
    min_len_list = []
    counter = 0
    uniprot_convert_df = pd.read_table(os.path.join('source_files', 'uniprot.tab'))
    uniprot_convert_df = uniprot_convert_df[[uniprot_convert_df.columns[0], 'Entry name']]
    uniprot_convert_df.columns = ['#ID', 'NAME']
    annotation = parse_annotation()
    uniprot_convert_df = uniprot_convert_df.apply(lambda x: add_meta(x, annotation), axis=1)
    uniprot_convert_df[
        uniprot_convert_df['family'].isna()][['#ID', 'NAME']].to_csv(
        os.path.join('files', 'exps_not_found_family.tsv'),
        sep='\t',
        index=False)
    tfs_len_dict = parse_hoco(uniprot_convert_df)
    for index, row in tqdm(uniprot_convert_df.iterrows()):
        tfs_len_list = tfs_len_dict['TFs'].get(row['NAME'])
        if not tfs_len_list:
            if row['subfamily'] is not None and row['subfamily'] != '{}' and tfs_len_dict['subfamily'].get(
                    row['subfamily']):
                tfs_len_list = tfs_len_dict['subfamily'].get(row['subfamily'])
            elif row['family'] is not None:
                tfs_len_list = tfs_len_dict['family'].get(row['family'], [])
                if row['family'] not in tfs_len_dict['family']:
                    counter += 1
            else:
                tfs_len_list = []
                counter += 1
        max_len_list.append(get_motif_length(tfs_len_list, 'max'))
        min_len_list.append(get_motif_length(tfs_len_list, 'min'))
    uniprot_convert_df['max_motif_len'] = max_len_list
    uniprot_convert_df['min_motif_len'] = min_len_list
    uniprot_convert_df.to_csv(os.path.join('files', 'len_annotated.tsv'),
                              index=False,
                              sep='\t')
    # print(counter)


if __name__ == '__main__':
    main()

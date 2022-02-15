import json
import os
import pandas as pd
from tqdm import tqdm

from cor import info_dict_path, initial_info_dict_path, bad_info_dict_path


def merge_info_dicts(human_info_dict, mouse_info_dict):
    tf_names = [*human_info_dict.keys(), *mouse_info_dict.keys()]
    result = {}
    for tf in tf_names:
        try:
            tf_without_suf, specie = tf.split('_')
        except ValueError:
            print(tf)
            raise
        if specie == 'HUMAN':
            new_value = human_info_dict[tf]
        elif specie == 'MOUSE':
            new_value = mouse_info_dict[tf]
        else:
            raise ValueError
        if new_value is None:
            print(tf)
        if tf_without_suf in result:
            result[tf_without_suf] = result[tf_without_suf].append(new_value)
        else:
            result[tf_without_suf] = new_value
    return result


def filter_array(motifs):
    words_tr = 50
    percent_tr = 0.25
    seqs_tr = 50
    good_motifs = []
    bad_motifs = []
    for x in motifs:
        if x['pcm_path'] and x['words'] >= words_tr \
                and x['total'] and x['seqs'] >= seqs_tr \
                and x['seqs'] / x['total'] >= percent_tr:
            good_motifs.append(x)
        else:
            bad_motifs.append(x)
    return good_motifs, bad_motifs


def main(merged_dict):
    # df = read_xlsx_master()
    # convert_d = pd.Series(df['curated:uniprot_id'].values,
    #                       index=df['curated:uniprot_ac']).to_dict()
    d = {}
    bad_d = {}
    print(merged_dict['KMT2A'])
    for key, value in tqdm(merged_dict.items()):
        new_key = key
        if new_key is None:
            continue
        if value is None:
            print(key)
        good_items, bad_items = filter_array(value)
        bad_d[new_key] = bad_items
        d[new_key] = good_items
    print('Dumping...')
    with open(info_dict_path, 'w') as out:
        json.dump(d, out, indent=2)
    with open(bad_info_dict_path, 'w') as out:
        json.dump(bad_d, out, indent=2)


if __name__ == '__main__':

    with open(initial_info_dict_path('human')) as r:
        human_info_dict = json.load(r)
    with open(initial_info_dict_path('mouse')) as r:
        mouse_info_dict = json.load(r)
    m_dict = merge_info_dicts(human_info_dict, mouse_info_dict)
    main(m_dict)

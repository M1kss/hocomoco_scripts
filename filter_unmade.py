import json
import os
import pandas as pd
from tqdm import tqdm

from cor import read_dicts, read_xlsx_master, info_dict_path, initial_info_dict_path, bad_info_dict_path


def read_uniprot_mapping():
    df = pd.read_table(os.path.join('source_files', 'uniprot.tab'))
    return pd.Series(df['Entry name'].values, index=df[df.columns[0]]).to_dict()


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


def filter_tfs():
    trans_dict = read_uniprot_mapping()
    dicts = read_dicts()
    d = {}
    # df = pd.read_excel('~/hocomoco_2021.xlsx')
    # curated_ids = info_dict.keys() - set(df['curated:uniprot_ac'].unique())
    # print(len(info_dict.keys()), len(set(x for x in info_dict.keys()) - curated_ids))
    # revert_dict = {}
    # for x in info_dict.keys():
    #     if x in trans_dict:
    #         revert_dict[trans_dict[x]] = x
    # tfs = set(trans_dict[x] for x in info_dict.keys() if x in trans_dict and sum([y['pcm_path'] is not None for y in info_dict[x]])) - set(df['curated:uniprot_id'].unique())
    # print(len(tfs))
    # with open('not_found.txt', 'w') as out:
    #     out.write('\n'.join(tfs))
    # print(len(curated_ids))
    # print(curated_ids - set([revert_dict[x] for x in tfs]))
    # sum_count = set()
    # for tf in tfs:
    #     tf_id = revert_dict[tf]
    #     sum_count |= set(x['name'] for x in info_dict[tf_id])
    # print('EXPS:', len(sum_count))
    for key in info_dict:
        new_key = trans_dict.get(key)
        if new_key is None:
            continue
        d[new_key] = [item for item in info_dict[key] if item['pcm_path'] is not None]
    # print([x for x in new_d.keys() if x is None])
    # df = pd.DataFrame({'TF': [x for x in sorted(list(new_d.keys()))],
    #                    'count': [len(new_d[x]) for x in sorted(list(new_d.keys()))]})
    # df = df.sort_values('count', ascending=False)
    # df = df[df['count'] > 0]
    # df.to_excel('motifs_stats.xlsx', index=False)
    # print(len(d))
    with open(os.path.expanduser('~/new_info.json'), 'w') as out:
        json.dump(d, out)


def main(i_dict):
    df = read_xlsx_master()
    convert_d = pd.Series(df['curated:uniprot_id'].values,
                          index=df['curated:uniprot_ac']).to_dict()
    d = {}
    bad_d = {}
    for key, value in tqdm(i_dict.items()):
        new_key = key
        if new_key is None:
            continue
        good_items, bad_items = filter_array(value)
        bad_d[new_key] = bad_items
        d[new_key] = good_items
    print('Dumping...')
    with open(info_dict_path, 'w') as out:
        json.dump(d, out, indent=2)
    with open(bad_info_dict_path, 'w') as out:
        json.dump(bad_d, out, indent=2)


if __name__ == '__main__':
    with open(initial_info_dict_path) as r:
        info_dict = json.load(r)
    main(info_dict)
import os
import json

import pandas as pd
from tqdm import tqdm

from cor import dicts_path, hocomoco_path, read_xlsx_master, read_cisbp_df, transform_name


def add_to_fam_dict(fam_dict, key, fam, df):
    if fam[key]:
        fam_tfs = df[df[key] == fam[key]]['curated:uniprot_id'].to_list()
        for tf in fam_tfs:
            if fam_dict.get(tf, None) is None:
                fam_dict[tf] = fam_tfs


def parse_known_tfs(tfs_df):
    family_dict = {}
    subfamily_dict = {}
    for index, row in tfs_df.iterrows():
        add_to_fam_dict(subfamily_dict, 'tfclass:subfamily', row, tfs_df)
        add_to_fam_dict(family_dict, 'tfclass:family', row, tfs_df)
    return family_dict, subfamily_dict


def choose_df_by_tf(cisbp_dfs, tf_name):
    if '_MOUSE' in tf_name:
        return cisbp_dfs['mouse'], 'mouse'
    elif '_HUMAN' in tf_name:
        return cisbp_dfs['human'], 'human'
    else:
        raise ValueError(tf_name)


def get_motifs_by_tf(cisbp_dfs, hoc_tf, tf_name, inferred=False):
    t, specie = choose_df_by_tf(cisbp_dfs, hoc_tf)
    motifs = t[t['TF_Name'] == tf_name]
    status_ok = {'D', 'I'} if inferred else {'D'}
    motifs = motifs[motifs['TF_Status'].isin(status_ok)]
    return motifs['Motif_ID'].tolist()


def get_family_motifs_by_tf(direct_dict, tfs_list):
    result = set()
    if tfs_list is None:
        return None
    for tf in tfs_list:
        if direct_dict.get(tf):
            tf_motifs = set(direct_dict.get(tf))
            result |= tf_motifs
    return list(result)


def get_hocomoco_by_tf(hocomoco_motifs, tf):
    return hocomoco_motifs.get(tf, [])


def read_hocomoco_dir():
    motifs = os.listdir(hocomoco_path)
    result = {}
    for motif in motifs:
        if motif != '.gitkeep':
            try:
                tf, _, _, qual, _ = motif.split('.')
            except ValueError:
                print(motif)
                raise
            result.setdefault(tf, []).append(motif)
    return result


def main():
    cisbp_dfs = read_cisbp_df()
    known_tfs = read_xlsx_master()
    tfs = known_tfs['auto:gene_symbol'].to_list()
    hocomoco_tfs = known_tfs['curated:uniprot_id'].to_list()
    hocomoco_tf_dict = {tfs[i]: hocomoco_tfs[i] for i in range(len(tfs))}
    tf_class_family_tfs_dict, tf_class_subfamily_tfs_dict = parse_known_tfs(known_tfs)
    direct_dict = {}
    inferred_dict = {}
    tf_class_family_dict = {}
    tf_class_subfamily_dict = {}
    print('Processing direct and inferred')
    for tf in tqdm(tfs):
        hoc_tf = hocomoco_tf_dict[tf]
        direct_dict[hoc_tf] = get_motifs_by_tf(cisbp_dfs, hoc_tf, tf)
        inferred_dict[hoc_tf] = get_motifs_by_tf(cisbp_dfs, hoc_tf, tf, inferred=True)
    with open(os.path.join(dicts_path, 'direct_dict.json'), 'w') as f:
        json.dump(direct_dict, f, indent=2)

    with open(os.path.join(dicts_path, 'inferred_dict.json'), 'w') as f:
        json.dump(inferred_dict, f, indent=2)
    print('Processing family, subfamily and HOCOMOCO')
    hocomoco_dict = {}
    hocomoco_motifs = read_hocomoco_dir()

    for hoc_tf in tqdm(hocomoco_tfs):
        tf_class_family_dict[hoc_tf] = get_family_motifs_by_tf(direct_dict,
                                                               tf_class_family_tfs_dict.get(hoc_tf, None))

        tf_class_subfamily_dict[hoc_tf] = get_family_motifs_by_tf(direct_dict,
                                                                  tf_class_subfamily_tfs_dict.get(hoc_tf, None))
        hocomoco_dict[hoc_tf] = get_hocomoco_by_tf(hocomoco_motifs, hoc_tf)
    with open(os.path.join(dicts_path, 'tf_class_family_dict.json'), 'w') as f:
        json.dump(tf_class_family_dict, f, indent=2)

    with open(os.path.join(dicts_path, 'tf_class_subfamily_dict.json'), 'w') as f:
        json.dump(tf_class_subfamily_dict, f, indent=2)
    with open(os.path.join(dicts_path, 'hocomoco_dict.json'), 'w') as f:
        json.dump(hocomoco_dict, f, indent=2)


if __name__ == '__main__':
    main()

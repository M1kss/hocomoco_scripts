import pandas as pd
import os
import json

from tqdm import tqdm

from cor import cisbp_human_dict_path, cisbp_mouse_dict_path, dicts_path, hocomoco_path


def get_tfs_by_fam_tf_class(fam, split_ids, dbid_dict, t, subfamily=False):
    if fam[-1] != 0:
        tfs = []
        for id in split_ids:
            if id[:(-1 if subfamily else -2)] == fam:
                tf_name = t[t['DBID'].isin(dbid_dict['.'.join(id)])]['TF_Name'].unique()
                if len(tf_name) == 0:
                    continue
                tfs.extend(tf_name)
        return list(set(tfs))
    else:
        return []


def add_to_fam_dict(fam_dict, key, fam, df):
    if fam:
        fam_tfs = df[df[key] == fam]['curated:uniprot_id']
        for tf in fam_tfs:
            if fam_dict.get(tf, None):
                fam_dict[tf] = fam_tfs
            else:
                fam_dict[tf] = None
    return fam_dict


def parse_known_tfs(tfs_df):
    family_dict = {}
    subfamily_dict = {}
    for index, row in tfs_df.iterrows():
        tf_subfamily = row['tfclass:subfamily']
        tf_family = row['tfclass:family']
        subfamily_dict = add_to_fam_dict(subfamily_dict, 'tfclass:subfamily', tf_subfamily, tfs_df)
        family_dict = add_to_fam_dict(family_dict, 'tfclass:family', tf_family, tfs_df)
    return family_dict, subfamily_dict


def chose_df_by_tf(cisbp_dfs, tf_name):
    if '_MOUSE' in tf_name:
        return cisbp_dfs['mouse']
    elif '_HUMAN' in tf_name:
        return cisbp_dfs['human']
    else:
        raise ValueError(tf_name)


def get_motifs_by_tf(cisbp_dfs, tf_name, inferred=False):
    t = chose_df_by_tf(cisbp_dfs, tf_name)
    motifs = t[t['TF_Name'] == tf_name]
    status_ok = {'D', 'I'} if inferred else {'D'}
    motifs = motifs[motifs['TF_Status'].isin(status_ok)]
    return motifs['Motif_ID'].tolist()


def get_family_motifs_by_tf(cisbp_dfs, tfs_list):
    result = set()
    if tfs_list is None:
        return None
    for tf in tfs_list:
        t = chose_df_by_tf(cisbp_dfs, tf)
        tf_motifs = t[t['TF_Name'] == tf]
        tf_motifs = set(tf_motifs[tf_motifs['TF_Status'] == 'D']['Motif_ID'].unique())
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
    cisbp_dfs = {specie: pd.read_table(fname) for
                 specie, fname in zip(['human', 'mouse'],
                                      [cisbp_human_dict_path, cisbp_mouse_dict_path])}
    known_tfs = pd.read_excel(os.path.join('source_files', 'hocomoco_2021.xlsx'),
                              engine='openpyxl')
    tfs = known_tfs['curated:uniprot_id'].to_list()
    tf_class_family_tfs_dict, tf_class_subfamily_tfs_dict = parse_known_tfs(known_tfs)
    print('parsed')
    direct_dict = {}
    inferred_dict = {}
    tf_class_family_dict = {}
    tf_class_subfamily_dict = {}
    hocomoco_dict = {}
    hocomoco_motifs = read_hocomoco_dir()
    for tf in tqdm(tfs):
        direct_dict[tf] = get_motifs_by_tf(cisbp_dfs, tf)
        inferred_dict[tf] = get_motifs_by_tf(cisbp_dfs, tf, inferred=True)
        tf_class_family_dict[tf] = get_family_motifs_by_tf(cisbp_dfs,
                                                           tf_class_family_tfs_dict[tf])

        tf_class_subfamily_dict[tf] = get_family_motifs_by_tf(cisbp_dfs,
                                                              tf_class_subfamily_tfs_dict[tf])

        hocomoco_dict[tf] = get_hocomoco_by_tf(hocomoco_motifs, tf)
    with open(os.path.join(dicts_path, 'direct_dict.json'), 'w') as f:
        json.dump(direct_dict, f, indent=2)

    with open(os.path.join(dicts_path, 'inferred_dict.json'), 'w') as f:
        json.dump(inferred_dict, f, indent=2)

    with open(os.path.join(dicts_path, 'tf_class_family_dict.json'), 'w') as f:
        json.dump(tf_class_family_dict, f, indent=2)

    with open(os.path.join(dicts_path, 'tf_class_subfamily_dict.json'), 'w') as f:
        json.dump(tf_class_subfamily_dict, f, indent=2)

    with open(os.path.join(dicts_path, 'hocomoco_dict.json'), 'w') as f:
        json.dump(hocomoco_dict, f, indent=2)


if __name__ == '__main__':
    main()

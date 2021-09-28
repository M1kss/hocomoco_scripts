import pandas as pd
import os
import json

from cor import cisbp_dict_path, dicts_path, hocomoco_path


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


def parse_tf_class(t, tfs):
    df = pd.read_table('source_files/tfclass.basic.tsv', header=None)
    ids = [gid.split(' ')[0] for gid in df[df[0] == 'genus'][1].unique()]
    split_ids = [tuple(gid.split('.')) for gid in ids]
    ann_df = pd.read_table('source_files/genus2ensuni_v3.tsv', header=None)
    ann_df = ann_df[ann_df.apply(lambda row: row[1].startswith('Homo_sapiens'), axis=1)]
    print(len(ann_df.index))
    dbid_dict = {}
    rev_dbid_dict = {}
    for gid in ids:
        value = ann_df[ann_df[0] == gid][2].unique()
        dbid_dict[gid] = list(value)
        for x in value:
            rev_dbid_dict[x] = gid
    tf_class_family_dict = {}
    tf_class_subfamily_dict = {}
    family_cache = {}
    subfamily_cache = {}
    for tf in tfs:
        dbids = t[t['TF_Name'] == tf]['DBID'].unique()
        if len(dbids) != 1:
            print(tf, dbids)
        dbid = dbids[0]
        gid = rev_dbid_dict.get(dbid)
        if not gid:
            tf_class_family_dict[tf] = []
            tf_class_subfamily_dict[tf] = []
            continue
        split_id = tuple(gid.split('.'))
        fam = split_id[:-2]
        subfam = split_id[:-1]
        fam_res = family_cache.get(fam)
        if fam_res:
            tf_class_family_dict[tf] = family_cache[fam]
        else:
            tf_class_family_dict[tf] = family_cache[fam] = get_tfs_by_fam_tf_class(fam, split_ids, dbid_dict, t, subfamily=False)
        subfam_res = subfamily_cache.get(subfam)
        if subfam_res:
            tf_class_subfamily_dict[tf] = subfamily_cache[subfam]
        else:
            tf_class_subfamily_dict[tf] = subfamily_cache[subfam] = get_tfs_by_fam_tf_class(subfam, split_ids, dbid_dict, t, subfamily=True)
    return tf_class_family_dict, tf_class_subfamily_dict


def get_motifs_by_tf(t, tf_name, inferred=False):
    motifs = t[t['TF_Name'] == tf_name]
    status_ok = {'D', 'I'} if inferred else {'D'}
    motifs = motifs[motifs['TF_Status'].isin(status_ok)]
    return motifs['Motif_ID'].tolist()


def get_family_motifs_by_tf(t, tf_name, family_motifs_dict, tf_class_dict=None):
    motifs = t[t['TF_Name'] == tf_name]
    family_names = motifs['Family_Name'].unique()
    assert len(family_names) == 1
    family_name = family_names[0]
    if family_name in family_motifs_dict:
        return family_motifs_dict[family_name]
    if tf_class_dict is None:
        family_tfs = t[t['Family_Name'] == family_name]['TF_Name'].unique()
    else:
        family_tfs = tf_class_dict[tf_name]
    all_motifs = []
    for tf in family_tfs:
        tf_motifs = t[t['TF_Name'] == tf]
        tf_motifs = tf_motifs[tf_motifs['TF_Status'] == 'D']['Motif_ID'].tolist()
        all_motifs.extend(tf_motifs)

    family_motifs = list(set(all_motifs))
    family_motifs_dict[family_name] = family_motifs
    return family_motifs


def get_hocomoco_by_tf(hocomoco_motifs, tf):
    return hocomoco_motifs.get(tf, [])


def read_hocomoco_dir():
    motifs = os.listdir(hocomoco_path)
    result = {}
    for motif in motifs:
        tf, _, _, qual, _ = motif.split('.')
        if tf == 'ANDR_HUMAN':
            tf = 'AR_HUMAN'
        if tf.endswith('_HUMAN'):
            tf = tf[:-6]
        result.setdefault(tf, []).append(motif)
    return result


def main():
    family_tfs_dict_cisbp = {}
    t = pd.read_table(cisbp_dict_path)
    tfs = t['TF_Name'].unique()
    tf_class_family_tfs_dict, tf_class_subfamily_tfs_dict = parse_tf_class(t, tfs)
    print('parsed')
    debug_t = t[t['TF_Status'] == 'I']
    print(debug_t)
    direct_dict = {tf: get_motifs_by_tf(t, tf) for tf in tfs}
    inferred_dict = {tf: get_motifs_by_tf(t, tf, inferred=True) for tf in tfs}
    family_dict = {tf: get_family_motifs_by_tf(t, tf, family_tfs_dict_cisbp) for tf in tfs}
    tf_class_family_dict = {tf: get_family_motifs_by_tf(t, tf, family_tfs_dict_cisbp, tf_class_family_tfs_dict)
                            for tf in tfs}
    tf_class_subfamily_dict = {tf: get_family_motifs_by_tf(t, tf, family_tfs_dict_cisbp, tf_class_subfamily_tfs_dict)
                               for tf in tfs}
    hocomoco_motifs = read_hocomoco_dir()
    hocomoco_dict = {tf: get_hocomoco_by_tf(hocomoco_motifs, tf) for tf in tfs}
    with open(os.path.join(dicts_path, 'direct_dict.json'), 'w') as f:
        json.dump(direct_dict, f)

    with open(os.path.join(dicts_path, 'inferred_dict.json'), 'w') as f:
        json.dump(inferred_dict, f)

    with open(os.path.join(dicts_path, 'family_dict.json'), 'w') as f:
        json.dump(family_dict, f)

    with open(os.path.join(dicts_path, 'tf_class_family_dict.json'), 'w') as f:
        json.dump(tf_class_family_dict, f)

    with open(os.path.join(dicts_path, 'tf_class_subfamily_dict.json'), 'w') as f:
        json.dump(tf_class_subfamily_dict, f)

    with open(os.path.join(dicts_path, 'hocomoco_dict.json'), 'w') as f:
        json.dump(hocomoco_dict, f)


if __name__ == '__main__':
    main()

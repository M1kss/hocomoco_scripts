import subprocess
import os
import sys
import json
import shutil
from multiprocessing import Pool

import pandas as pd

dicts_path = 'files'
cisbp_human_dict_path = os.path.join('source_files', 'TF_Information_human.txt')
cisbp_mouse_dict_path = os.path.join('source_files', 'TF_Information_mouse.txt')
info_dict_path = os.path.join('files', 'filtered_info.json')
bad_info_dict_path = os.path.join('files', 'no_info.json')

result_path = 'ape_result'
motif_dir = 'cisbp_pwms'

dict_types = ['hocomoco', 'direct', 'inferred', 'tf_class_subfamily', 'tf_class_family']

ape_path = os.path.expanduser('~/ape.jar')
hocomoco_path = 'hocomoco_pwms'
allowed_tfs = ['ANDR']

species = 'human', 'mouse'


def initial_info_dict_path(specie):
    return os.path.join('files', 'info.{}.json'.format(specie))


def read_xlsx_master():
    return pd.read_excel(os.path.join('source_files', 'hocomoco_2021.xlsx'),
                         engine='openpyxl')


def read_info_dict(path=None):
    if path is None:
        path = info_dict_path
    with open(path) as info:
        return json.load(info)


def check_dir_for_collection(tf, motif_collection, d_type, to_copy=True):
    dir_path = os.path.join(result_path, tf + '_' + d_type)
    if motif_collection is None:
        return None
    if to_copy:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.mkdir(dir_path)
    paths = []
    for motif in motif_collection:
        if d_type == 'hocomoco':
            path = os.path.join(hocomoco_path, motif)
        else:
            path = os.path.join(motif_dir, motif + '.ppm')
        if to_copy:
            if os.path.exists(path):
                shutil.copy2(path, dir_path)
            else:
                pass
        else:
            paths.append(path)
    if to_copy:
        return dir_path
    else:
        return paths


def parse_output(exp, output):
    pcm_name = os.path.splitext(os.path.basename(exp))[0]
    best_motif = {}
    for line in output.split('\n'):
        if line.startswith('#') or not line:
            continue
        motif, similarity, shift, overlap, orientation = line.strip('\n').split('\t')
        if not best_motif or best_motif['similarity'] < float(similarity):
            best_motif = {'motif': motif,
                          'similarity': float(similarity),
                          'shift': shift,
                          'overlap': overlap,
                          'orientation': orientation}
    return pcm_name, best_motif


def run_ape(exps, res_dir, d_type, jobs=1):
    result = {}
    if res_dir is not None:
        exps_batches = [exps[i:i + jobs] for i in range(0, len(exps), jobs)]

        for batch in exps_batches:
            commands = [["java", '-cp', ape_path,
                         'ru.autosome.macroape.ScanCollection',
                         exp, res_dir, '--query-pcm',
                         '--collection-{}'.format('pcm' if d_type == 'hocomoco' else 'ppm'),
                         '-d', '1', '--all'] for exp in batch]
            processes = [subprocess.Popen(command,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE) for command in commands]
            for process in processes:
                process.wait()
            for process, exp in zip(processes, batch):
                err = process.stderr.read().decode('utf-8')
                if err and not err.startswith('Warning!'):
                    print(err)
                    print(exp)
                    raise ValueError
                res = process.stdout.read().decode('utf-8')
                name, res = parse_output(exp, res)
                result[name] = res
        shutil.rmtree(res_dir)
    return result


def read_dicts():
    dicts = {}
    for d_type in dict_types:
        with open(os.path.join(dicts_path, d_type + '_dict.json')) as f:
            dicts[d_type] = json.load(f)
    return dicts


def transform_name(tf, specie):
    tf_name = tf.split('_')[0]
    if tf_name == 'ANDR':
        tf_name = 'AR'
    if specie == 'human':
        return tf_name
    elif specie == 'mouse':
        return tf_name.lower().capitalize()
    else:
        raise ValueError(specie)


def read_cisbp_df():
    return {specie: pd.read_table(fname) for
            specie, fname in zip(['human', 'mouse'],
                                 [cisbp_human_dict_path, cisbp_mouse_dict_path])}


def process_tf(tf, d_type, dicts, info_dict):
    pwms = {}
    for specie in species:
        pwms[specie] = [x['pcm_path'] for x in info_dict[tf] if x['specie'] == specie]
    results = {}
    if d_type == 'hocomoco':
        tf_name = tf + '_' + 'HUMAN'
        motif_collection = dicts[d_type].get(tf_name, None)
        if not motif_collection:
            tf_name = tf + '_' + 'MOUSE'
            motif_collection = dicts[d_type].get(tf_name, None)
        if not motif_collection:
            return
    else:
        motif_collection = []
        for specie in species:
            tf_name = tf + '_' + specie.upper()
            motif_col = dicts[d_type].get(tf_name, None)
            if motif_col is not None:
                motif_collection += motif_col
        motif_collection = set(motif_collection)
    res_dir = check_dir_for_collection(tf, motif_collection, d_type)
    ape_res = run_ape([x['pcm_path'] for x in info_dict[tf]], res_dir, d_type)
    results[d_type] = ape_res
    return results


def main(njobs=10):
    dicts = read_dicts()
    info_dict = read_info_dict()
    tfs = info_dict.keys()
    results = {}
    with Pool(njobs) as p:
        for tf, res in zip(tfs, p.starmap(process_tf, [(tf, d_type, dicts, info_dict)
                                                       for tf in tfs for d_type in dict_types])):
            if res is None:
                continue
            print(f'Doing {tf}')
            results.setdefault(tf, {}).update(res)

    for tf in results:
        with open(os.path.join(result_path, f'{tf}.json'), 'w') as out:
            json.dump(results[tf], out, indent=2)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 0 else 1)

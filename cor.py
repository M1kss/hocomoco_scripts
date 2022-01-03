import subprocess
import os
import sys
import json
import shutil
import pandas as pd

from tqdm import tqdm

dicts_path = 'files'
cisbp_human_dict_path = os.path.join('source_files', 'TF_Information_human.txt')
cisbp_mouse_dict_path = os.path.join('source_files', 'TF_Information_mouse.txt')
info_dict_path = os.path.join('files', 'filtered_info.json')
initial_info_dict_path = os.path.join('files', 'info.json')
result_path = 'ape_result'
motif_dir = 'cisbp_pwms'

dict_types = ['hocomoco', 'direct', 'inferred', 'tf_class_family', 'tf_class_subfamily']

ape_path = os.path.expanduser('~/ape.jar')
hocomoco_path = 'hocomoco_pwms'
allowed_tfs = ['ANDR_MOUSE', 'CTCF_MOUSE']


def read_xlsx_master():
    return pd.read_excel(os.path.join('source_files', 'hocomoco_2021.xlsx'),
                         engine='openpyxl')


def check_dir_for_collection(tf, motif_collection, d_type):
    dir_path = os.path.join(result_path, tf + '_' + d_type)
    if motif_collection is None:
        return None
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.mkdir(dir_path)
    for motif in motif_collection:
        if d_type == 'hocomoco':
            path = os.path.join(hocomoco_path, motif)
        else:
            path = os.path.join(motif_dir, motif + '.txt')
        if os.path.exists(path):
            shutil.copy2(path, dir_path)
        else:
            pass
    return dir_path


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


def run_ape(exps, res_dir, jobs=10):
    result = {}
    if res_dir is not None:
        exps_batches = [exps[i:i + jobs] for i in range(0, len(exps), jobs)]

        for batch in exps_batches:
            commands = [["java", '-cp', ape_path,
                         'ru.autosome.macroape.ScanCollection',
                         exp, res_dir, '--query-pcm', '-d', '1', '--all'] for exp in batch]
            processes = [subprocess.Popen(command,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE) for command in commands]
            for process in processes:
                process.wait()
            for process, exp in zip(processes, batch):
                res = process.stdout.read().decode('utf-8')
                print(res)
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


def transform_name(tf):
    return tf


def filter_pwms(motifs):
    words_tr = 50
    percent_tr = 0.25
    return [x for x in motifs if x['pcm_path']
            and x['words'] >= words_tr and x['total'] and x['seqs'] / x['total'] >= percent_tr]


def main(njobs=10):
    dicts = read_dicts()
    with open(info_dict_path) as info:
        info_dict = json.load(info)
    for tf in tqdm(info_dict.keys()):
        if allowed_tfs is not None:
            if tf not in allowed_tfs:
                continue
        if os.path.exists(os.path.join('reports', tf + '.xlsx')):
            continue
        results = {}
        pwms = [x['pcm_path'] for x in filter_pwms(info_dict[tf])]
        for d_type in dict_types:
            motif_collection = dicts[d_type].get(tf)
            if not motif_collection and d_type != 'hocomoco':
                continue
            res_dir = check_dir_for_collection(tf, motif_collection, d_type)
            ape_res = run_ape(pwms, res_dir, njobs)
            results[d_type] = ape_res
        with open(os.path.join(result_path, tf + '.json'), 'w') as out:
            json.dump(results, out, indent=2)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 0 else 1)

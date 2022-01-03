import subprocess
import os
import sys
import json
import shutil

dicts_path = 'files'
cisbp_human_dict_path = os.path.join('source_files', 'TF_Information_human.txt')
cisbp_mouse_dict_path = os.path.join('source_files', 'TF_Information_mouse.txt')
info_dict_path = os.path.join('files', 'new_info.json')
result_path = 'ape_result'
motif_dir = 'cisbp_pwms'

dict_types = ['hocomoco', 'direct', 'inferred', 'tf_class_family', 'tf_class_subfamily']


ape_path = os.path.expanduser('~/ape.jar')
hocomoco_path = 'hocomoco_pwms'
allowed_tfs = ['ANDR_MOUSE', 'CTCF_MOUSE']


def check_dir_for_collection(tf, motif_collection, d_type):
    dir_path = os.path.join(result_path, tf + '_' + d_type)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.mkdir(dir_path)
    for motif in motif_collection:
        if d_type == 'hocomoco':
            path = os.path.join('pcm', motif)
        else:
            path = os.path.join(motif_dir, motif + '.ppm')
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


def run_ape(exps, res_dir, jobs=10, additional_message=''):
    result = {}
    exps_batches = [exps[i:i + jobs] for i in range(0, len(exps), jobs)]

    for index, batch in enumerate(exps_batches, 1):
        print('Doing {}/{} batch {}'.format(index, len(exps_batches), additional_message))
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
    if tf == 'ANDR_HUMAN':
        result = 'AR'
    else:
        result = tf[:-6] if tf.endswith('_HUMAN') else tf
    return result


def filter_pwms(motifs):
    words_tr = 50
    percent_tr = 0.25
    return [x for x in motifs if x['pcm_path']
            and x['words'] >= words_tr and x['total'] and x['seqs']/x['total'] >= percent_tr]


def main(njobs=10):
    dicts = read_dicts()
    with open(info_dict_path) as info:
        info_dict = json.loads(info.readline())
    hoco_dict = [x for x, y in dicts['hocomoco'].items() if len(y) > 0]
    for index, tf_name in enumerate(hoco_dict):
        tf = tf_name + '_HUMAN'
        if os.path.exists(os.path.join('reports', tf + '.xlsx')):
            continue
        results = {}
        if tf not in info_dict:
            continue
        pwms = [x['pcm_path'] for x in filter_pwms(info_dict[tf])]
        t_name = transform_name(tf)
        for d_type in dict_types:
            if len(pwms) > 1000 and d_type != 'hocomoco':
                continue
            motif_collection = dicts[d_type].get(t_name)
            if not motif_collection:
                continue
            res_dir = check_dir_for_collection(tf, motif_collection, d_type)
            additional_message = 'for {} {} ({}/{})'.format(tf, d_type, index, len(hoco_dict))
            ape_res = run_ape(pwms, res_dir, njobs, additional_message)
            results[d_type] = ape_res
        with open(os.path.join(result_path, tf + '.json'), 'w') as out:
            json.dump(results, out)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 0 else 1)

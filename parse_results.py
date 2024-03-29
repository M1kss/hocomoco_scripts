import os
import json
import sys

import pandas as pd
from tqdm import tqdm

from cor import initial_info_dict_path


def get_time(time):
    if time < 60:
        return str(round(time)) + 's'
    elif time < 3600:
        return str(round(time / 60)) + 'm'
    else:
        return str(round(time / 3600)) + 'h'


def parse_one_file(file_name, outputs_dir, specie):
    peaks, caller, best_by, motif_type, _ = file_name.split('.')
    with open(os.path.join(outputs_dir, 'results', file_name)) as f:
        parsed_output = []
        last_line = None
        for line in f:
            try:
                key, value = line.strip('\n').split('|')
            except ValueError:
                continue
            parsed_output.append((key, value))
            last_line = line
        if last_line is None or not last_line.startswith('_^^_| P0wered by cute chipmunks!'):
            return [{
                'specie': specie,
                'name': peaks,
                'caller': caller,
                'motif_type': motif_type,
                'selected_by': best_by,
                'words': 0,
                'words_lines': [],
                'motif_index': None,
                'motif_len': None,
                'diag': ['Unexpected interrupt'],
                'time': None,
                'pcm_path': None,
            }]

    A = [value.split(' ') for key, value in parsed_output if key == 'A']
    C = [value.split(' ') for key, value in parsed_output if key == 'C']
    G = [value.split(' ') for key, value in parsed_output if key == 'G']
    T = [value.split(' ') for key, value in parsed_output if key == 'T']
    DIAG = [value for key, value in parsed_output if key == 'DIAG' and value.startswith('fail')]

    if len(A) == 0:
        if len(parsed_output) != 0:
            return [{
                'specie': specie,
                'name': peaks,
                'caller': caller,
                'motif_type': motif_type,
                'selected_by': best_by,
                'words': 0,
                'seqs': 0,
                'total': 0,
                'motif_index': None,
                'motif_len': None,
                'words_lines': [],
                'diag': ['Unexpected interrupt'],
                'time': None,
                'pcm_path': None,
            }]
        return [{
            'specie': specie,
            'name': peaks,
            'caller': caller,
            'motif_type': motif_type,
            'selected_by': best_by,
            'motif_index': None,
            'motif_len': None,
            'words_lines': [],
            'words': 0,
            'total': 0,
            'seqs': 0,
            'diag': DIAG,
            'time': None,
            'pcm_path': None,
        }]

    result = []

    ACGT = list(zip(A, C, G, T))
    TIME = [float(value) for key, value in parsed_output if key == 'TIME'][-1]
    time = get_time(TIME)
    total = sum(1 for line in open(os.path.join(outputs_dir, 'fasta', '.'.join([peaks, caller, best_by, 'mfa']))))
    assert total % 2 == 0
    total = total // 2
    for i, quad in enumerate(ACGT):
        if quad in ACGT[:i]:
            assert len(ACGT) == 2 * i
            ACGT = ACGT[:i]
            break
    for k, quad in enumerate(ACGT):
        pcm_path = os.path.join('results', '{}.{}.pcm'.format(file_name[:-4], k))
        with open(pcm_path, 'w') as pcm:
            pcm.write('>{}.{}'.format(file_name[:-4], k) + '\n')
            values = list(zip(*quad))
            motif_len = len(values)
            words = [float(value) for key, value in parsed_output if key == 'WRDS'][k]
            seqs = [float(value) for key, value in parsed_output if key == 'SEQS'][k]
            words_lines = []
            check_output = False
            counter = 0
            for key, value in parsed_output:
                if check_output and key == 'LENG':
                    counter += 1
                    check_output = False
                elif check_output or key == 'LIST':
                    assert key in ('WORD', 'LIST')
                    if counter == k:
                        words_lines.append(value)
                    check_output = True

            for a, c, g, t in values:
                pcm.write('\t'.join([a, c, g, t]) + '\n')
        result.append({
            'specie': specie,
            'name': peaks,
            'caller': caller,
            'motif_type': motif_type,
            'selected_by': best_by,
            'words': words,
            'words_lines': words_lines,
            'seqs': seqs,
            'total': total,
            'motif_index': k,
            'motif_len': motif_len,
            'diag': DIAG,
            'time': time,
            'pcm_path': pcm_path,
        })
    return result


def make_tfs_dict(master_list):
    out = {}
    master = pd.read_csv(master_list, header=None)
    master.columns = ['specie', 'tf', 'peaks', '1', '2', '3', '4', '5']
    for tf in master['tf'].unique():
        for peak in master[master['tf'] == tf]['peaks'].to_list():
            out[peak] = tf
    return out


def main(outputs_dir, master_list, specie='human'):
    tfs_dict = make_tfs_dict(master_list)
    results = {}
    iterable = os.listdir(os.path.join(outputs_dir, 'results'))
    for file_name in tqdm(iterable, total=len(iterable)):
        peaks = file_name.split('.')[0]
        if peaks not in tfs_dict:
            continue
        info = parse_one_file(file_name, outputs_dir, specie)
        results.setdefault(tfs_dict[peaks], []).extend(info)
    with open(initial_info_dict_path(specie), 'w') as ot:
        json.dump(results, ot, indent=2)


if __name__ == '__main__':
    assert sys.argv[3] in ('human', 'mouse')
    main(sys.argv[1], sys.argv[2], sys.argv[3])

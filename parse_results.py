import os
import json
import pandas as pd


def get_time(time):
    if time < 60:
        return str(round(time)) + 's'
    elif time < 3600:
        return str(round(time / 60)) + 'm'
    else:
        return str(round(time / 3600)) + 'h'


results_dir = os.path.expanduser('~/hocomoco/')
outputs_dir = os.path.join(results_dir, 'results')
pcms_dir = os.path.expanduser('~/hocomoco-pcms/')
master_path = os.path.expanduser('~/hocomoco/hoco-master-human.tsv')


def parse_one_file(file_name):
    peaks, caller, best_by, motif_type, _ = file_name.split('.')
    with open(os.path.join(outputs_dir, file_name)) as f:
        parsed_output = []
        last_line = None
        for line in f:
            key, value = line.strip('\n').split('|')
            parsed_output.append((key, value))
            last_line = line
        if last_line is None or not last_line.startswith('_^^_| P0wered by cute chipmunks!'):
            print(last_line)
            return [{
                'name': peaks,
                'caller': caller,
                'motif_type': motif_type,
                'selected_by': best_by,
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
        assert len(parsed_output) == 0
        return [{
            'name': peaks,
            'caller': caller,
            'motif_type': motif_type,
            'selected_by': best_by,
            'motif_index': None,
            'motif_len': None,
            'diag': DIAG,
            'time': None,
            'pcm_path': None,
        }]

    result = []

    ACGT = list(zip(A, C, G, T))
    TIME = [float(value) for key, value in parsed_output if key == 'TIME'][-1]
    time = get_time(TIME)
    for i, quad in enumerate(ACGT):
        if quad in ACGT[:i]:
            assert len(ACGT) == 2 * i
            ACGT = ACGT[:i]
            break
    for k, quad in enumerate(ACGT):
        pcm_path = os.path.join(pcms_dir, '{}.{}.pcm'.format(file_name[:-4], k))
        with open(pcm_path, 'w') as pcm:
            pcm.write('>{}.{}'.format(file_name[:-4], k) + '\n')
            values = list(zip(*quad))
            motif_len = len(values)
            for a, c, g, t in values:
                pcm.write('\t'.join([a, c, g, t]) + '\n')
        result.append({
            'name': peaks,
            'caller': caller,
            'motif_type': motif_type,
            'selected_by': best_by,
            'motif_index': k,
            'motif_len': motif_len,
            'diag': DIAG,
            'time': time,
            'pcm_path': pcm_path,
        })
    return result


def make_tfs_dict():
    out = {}
    master = pd.read_csv(master_path, header=None)
    master.columns = ['specie', 'tf', 'peaks', '1', '2', '3', '4', '5']
    for tf in master['tf'].unique():
        for peak in master[master['tf'] == tf]['peaks'].to_list():
            out[peak] = tf
    return out


def main():
    tfs_dict = make_tfs_dict()
    results = {}
    for file_name in os.listdir(outputs_dir):
        peaks = file_name.split('.')[0]
        info = parse_one_file(file_name)
        results.setdefault(tfs_dict[peaks], []).extend(info)
    with open(os.path.expanduser('~/info.json'), 'w') as ot:
        json.dump(results, ot)


if __name__ == '__main__':
    if not os.path.isdir(pcms_dir):
        os.mkdir(pcms_dir)
    main()

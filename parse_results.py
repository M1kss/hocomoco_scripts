import os
import json

def get_time(time):
    if time < 60:
        return str(round(time)) + 's'
    elif time < 3600:
        return str(round(time / 60)) + 'm'
    else:
        return str(round(time / 3600)) + 'h'


results_dir = os.path.expanduser('~/results_SP1/')
outputs_dir = os.path.join(results_dir, 'results')
pcms_dir = os.path.expanduser('~/pcms_SP1/')

if not os.path.isdir(pcms_dir):
    os.mkdir(pcms_dir)

info = []

for file in os.listdir(outputs_dir):
    print(file)
    peaks, caller, best_by, motif_type, _ = file.split('.')
    with open(os.path.join(outputs_dir, file)) as f:
        parsed_output = []
        for line in f:
            key, value = line.strip('\n').split('|')
            parsed_output.append((key, value))
    A = [value.split(' ') for key, value in parsed_output if key == 'A']
    C = [value.split(' ') for key, value in parsed_output if key == 'C']
    G = [value.split(' ') for key, value in parsed_output if key == 'G']
    T = [value.split(' ') for key, value in parsed_output if key == 'T']
    DIAG = [value for key, value in parsed_output if key == 'DIAG' and value.startswith('fail')]
    if len(A) == 0:
        assert len(parsed_output) == 0
        info.append({
            'name': peaks,
            'caller': caller,
            'motif_type': motif_type,
            'selected_by': best_by,
            'motif_index': None,
            'motif_len': None,
            'diag': DIAG,
            'time': None,
            'pcm_path': None,
        })
        continue
    ACGT = list(zip(A, C, G, T))
    TIME = [float(value) for key, value in parsed_output if key == 'TIME'][-1]
    time = get_time(TIME)
    for i, quad in enumerate(ACGT):
        if quad in ACGT[:i]:
            assert len(ACGT) == 2*i
            ACGT = ACGT[:i]
            break
    for k, quad in enumerate(ACGT):
        pcm_path = os.path.join(pcms_dir, '{}.{}.pcm'.format(file[:-4], k))
        with open(pcm_path, 'w') as pcm:
            pcm.write('>{}.{}'.format(file[:-4], k) + '\n')
            values = list(zip(*quad))
            motif_len = len(values)
            for a, c, g, t in values:
                pcm.write('\t'.join([a, c, g, t]) + '\n')
        info.append({
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
with open(os.path.expanduser('~/info.json'), 'w') as ot:
    json.dump({'SP1_HUMAN': info}, ot)

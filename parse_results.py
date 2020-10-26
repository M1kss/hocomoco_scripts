import os
import json

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
    if DIAG:
        print(DIAG)
    if len(A) == 0:
        assert len(parsed_output) == 0
        continue
    ACGT = list(zip(A, C, G, T))
    for i, quad in enumerate(ACGT):
        if quad in ACGT[:i]:
            assert len(ACGT) == 2*i
            ACGT = ACGT[:i]
            break
    for k, quad in enumerate(ACGT):
        with open(os.path.join(pcms_dir, '{}.{}.pcm'.format(file[:-4], k)), 'w') as pcm:
            pcm.write('>{}.{}'.format(file[:-4], k) + '\n')
            for a, c, g, t in zip(quad):
                pcm.write(''.join([a, c, g, t, '\n']))
    # info.append({
    #
    # })
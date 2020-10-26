import os
import json

results_dir = os.path.expanduser('~/results_SP1/')
outputs_dir = os.path.join(results_dir, 'results')

info = []

for file in os.listdir(outputs_dir):
    print(file)
    peaks, caller, best_by, motif_type, _ = file.split('.')
    with open(os.path.join(outputs_dir, file)) as f:
        parsed_output = []
        for line in f:
            key, value = line.strip('\n').split('|')
            parsed_output.append((key, value))
    A = [value for key, value in parsed_output if key == 'A']
    C = [value for key, value in parsed_output if key == 'C']
    G = [value for key, value in parsed_output if key == 'G']
    T = [value for key, value in parsed_output if key == 'T']
    if len(A) == 0:
        assert len(parsed_output) == 0
        continue
    ACGT = list(zip(A, C, G, T))
    for i, quad in enumerate(ACGT):
        if quad in ACGT[:i]:
            assert len(ACGT) == 2*i
            break
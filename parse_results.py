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
    A0 = A[0]
    try:
        for a in A:
            assert a == A0
    except AssertionError:
        print(A)
        raise
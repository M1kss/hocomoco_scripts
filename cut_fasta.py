import sys
import numpy as np
import pandas as pd
from collections import deque
import os

chr_l = [248956422, 242193529, 198295559, 190214555, 181538259, 170805979, 159345973,
         145138636, 138394717, 133797422, 135086622, 133275309, 114364328, 107043718,
         101991189, 90338345, 83257441, 80373285, 58617616, 64444167, 46709983, 50818468,
         156040895, 57227415]


class ChromPos:
    chrs = dict(zip(['chr' + str(i) for i in range(1, 23)] + ['chrX', 'chrY'], chr_l))
    genome_length = sum(chr_l)


def main(peaks, genome_file_name, out_file_name):
    num = dict(zip(['A', 'a', 'C', 'c', 'G', 'g', 'T', 't'], [1, 1, 2, 2, 3, 3, 4, 4]))
    nuc = dict(zip([1, 2, 3, 4, 5], ['A', 'C', 'G', 'T', 'N']))

    start_end_positions_queues = dict()
    genome_nucleotides_dict = dict()

    peaks_df = pd.read_table(peaks, names=['#CHR', 'START', 'END', 'SUMMIT'])

    if peaks_df.empty:
        print('empty peaks, {}'.format(peaks))
        exit(1)

    for chr_name in ChromPos.chrs:
        start_end_positions_queues[chr_name] = deque()
        genome_nucleotides_dict[chr_name] = np.zeros(ChromPos.chrs[chr_name], np.int8)

    for index, row in peaks_df.iterrows():
        start_end_positions_queues[row['#CHR']].append({'start': row['START'], 'end': row['END']})

    p = 0
    skip_to_next_chr = False
    with open(genome_file_name) as genome:
        for line in genome:
            if line[0] == '>':
                chr = line[1:-1]
                if chr not in ChromPos.chrs:
                    skip_to_next_chr = True
                    continue
                else:
                    skip_to_next_chr = False
                p = 0

                next_1 = {'start': 0, 'end': 0}
                next_2 = {'start': 0, 'end': 0}

                next_start = 0
                next_end = 0

                if start_end_positions_queues[chr]:
                    next_1 = start_end_positions_queues[chr].popleft()
                    next_start = next_1['start']
                    next_end = next_1['end']
                    # print(next_start, next_end)
                    if start_end_positions_queues[chr]:
                        next_2 = start_end_positions_queues[chr].popleft()
                        # print(next_2)
                        while next_end >= next_2['start']:
                            next_end = next_2['end']
                            if start_end_positions_queues[chr]:
                                next_2 = start_end_positions_queues[chr].popleft()
                            else:
                                break
                else:
                    skip_to_next_chr = True
            else:
                if skip_to_next_chr:
                    continue
                if p < next_start - 110:
                    p += 100

                    continue
                for sym in line.strip():
                    p += 1

                    if p > next_end:
                        if start_end_positions_queues[chr]:
                            next_1 = next_2
                            next_start = next_1['start']
                            next_end = next_1['end']
                            if start_end_positions_queues[chr]:
                                next_2 = start_end_positions_queues[chr].popleft()
                                while next_end >= next_2['start']:
                                    # print('a-haa!', p, next_start, next_end, next_2-(motive_length - 1))
                                    next_end = next_2['end']
                                    if start_end_positions_queues[chr]:
                                        next_2 = start_end_positions_queues[chr].popleft()
                                    else:
                                        break
                        else:
                            if next_2:
                                next_1 = next_2
                                next_2 = 0
                                next_start = next_1['start']
                                next_end = next_1['end']
                            else:
                                skip_to_next_chr = True
                                break
                    if next_start <= p <= next_end:
                        genome_nucleotides_dict[chr][p] = num.get(sym.lower(), 5)

    with open(out_file_name, 'w') as out:
        for index, row in peaks_df.iterrows():
            out.write('> {}\n'.format(row['SUMMIT']))
            out.write(''.join([nuc[genome_nucleotides_dict[row['#CHR']][i]] for i in range(row['START'], row['END'] + 1)]) + '\n')


if __name__ == '__main__':
    main(genome_file_name=os.path.expanduser(sys.argv[1]), peaks=os.path.expanduser(sys.argv[2]), out_file_name=os.path.expanduser(sys.argv[3]))

import os
import sys

base_dir = sys.argv[1]
out_dir = sys.argv[2]
if not os.path.exists(out_dir):
    os.mkdir(out_dir)
fasta_dir = os.path.join(base_dir, 'fasta')

for peak in os.listdir(fasta_dir):
    peak_name, caller, score, *args = peak.split('.')
    df_name = '.'.join([peak_name, caller, score, 'sorted', 'bed'])
    if caller == 'gem':
        print('Now doing:', peak)
        with open(os.path.join(fasta_dir, peak)) as f,\
                open(os.path.join(out_dir, peak), 'w') as out:
            for index, line in enumerate(f):
                if index % 2 == 1:
                    out.write(line)
                else:
                    line = line.strip()
                    out.write('> 151\n')

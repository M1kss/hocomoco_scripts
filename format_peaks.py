import pandas as pd
import sys
import os

chr_l = [248956422, 242193529, 198295559, 190214555, 181538259, 170805979, 159345973,
         145138636, 138394717, 133797422, 135086622, 133275309, 114364328, 107043718,
         101991189, 90338345, 83257441, 80373285, 58617616, 64444167, 46709983, 50818468,
         156040895, 57227415]


class ChromPos:
    chrs = dict(zip(['chr' + str(i) for i in range(1, 23)] + ['chrX', 'chrY'], chr_l))
    genome_length = sum(chr_l)


peaks_types = {
    'cpics',
    'macs',
    'gem',
    'macs2',
    'macs2-nomodel',
    'sissrs'
}


def check_row(df_row):
    return (df_row['CHR'] in ChromPos.chrs) and df_row['START'] > 0 and df_row['END'] > 0


def main(peak_file_name, peak_type, out_path):
    assert peak_type in peaks_types
    peak_df = pd.read_table(peak_file_name)
    if peak_df.empty:
        print('empty peaks, {}'.format(peak_file_name))
        exit(1)
    if peak_type == 'cpics' or peak_type == 'sissrs':
        peak_df['SUMMIT'] = (peak_df['END'] - peak_df['START']) // 2
    elif peak_type == 'macs':
        peak_df['SUMMIT'] = peak_df['summit']
    elif peak_type == 'gem':
        peak_df['SUMMIT'] = peak_df['END']
        peak_df['START'] = peak_df['START'].apply(lambda x: max(x - 150, 0))
        peak_df['END'] = peak_df['END'] + 150
    elif peak_type == 'macs2' or peak_type == 'macs2-nomodel':
        peak_df['SUMMIT'] = peak_df['abs_summit'] - peak_df['START']

    peak_df['CHR'] = peak_df['#CHROM'].apply(lambda x: 'chr' + str(x))
    peak_df = peak_df[peak_df.apply(check_row, axis=1)]
    if peak_df.empty:
        print('empty peaks, {}'.format(peak_file_name))
        exit(1)
    peak_df[['CHR', 'START', 'END', 'SUMMIT']].to_csv(out_path, sep='\t', index=False)


if __name__ == '__main__':
    main(peak_file_name=os.path.expanduser(sys.argv[1]), peak_type=sys.argv[2], out_path=os.path.expanduser(sys.argv[3]))

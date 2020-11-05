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

score_types = {
    'score',
    'pvalue'
}


def check_row(df_row):
    return (df_row['#CHR'] in ChromPos.chrs) and df_row['START'] > 0 and df_row['END'] > 0


def main(peak_file_name, peak_type, score_type, out_path):
    assert peak_type in peaks_types
    assert score_type in score_types
    peak_df = pd.read_table(peak_file_name)
    if peak_df.empty:
        print('empty peaks, {}'.format(peak_file_name))
        exit(1)
    if peak_type == 'cpics' or peak_type == 'sissrs':
        peak_df['SUMMIT'] = (peak_df['END'] - peak_df['START']) // 2
        if peak_type == 'cpics':
            assert score_type == 'score'
            peak_df['SCORE'] = peak_df['score']
            peak_df['SCORE2'] = peak_df['score']
        elif peak_type == 'sissrs':
            if score_type == 'score':
                peak_df['SCORE'] = peak_df['NumTags']
                peak_df['SCORE2'] = peak_df['p-value']
            elif score_type == 'pvalue':
                peak_df['SCORE'] = peak_df['p-value']
                peak_df['SCORE2'] = peak_df['NumTags']
    elif peak_type == 'macs':
        peak_df['SUMMIT'] = peak_df['summit']
        if score_type == 'score':
            peak_df['SCORE'] = peak_df['tags']
            peak_df['SCORE2'] = peak_df['-10*log10(pvalue)']
        elif score_type == 'pvalue':
            peak_df['SCORE'] = peak_df['-10*log10(pvalue)']
            peak_df['SCORE2'] = peak_df['tags']
    elif peak_type == 'gem':
        peak_df['SUMMIT'] = peak_df['END']
        peak_df['START'] = peak_df['START'].apply(lambda x: max(x - 150, 0))
        peak_df['END'] = peak_df['END'] + 150
        if score_type == 'score':
            peak_df['SCORE'] = peak_df['IP']
            peak_df['SCORE2'] = peak_df['P_-lg10']
        elif score_type == 'pvalue':
            peak_df['SCORE'] = peak_df['P_-lg10']
            peak_df['SCORE2'] = peak_df['IP']
    elif peak_type == 'macs2' or peak_type == 'macs2-nomodel':
        peak_df['SUMMIT'] = peak_df['abs_summit'] - peak_df['START']
        if score_type == 'score':
            peak_df['SCORE'] = peak_df['pileup']
            peak_df['SCORE2'] = peak_df['-log10(pvalue)']
        elif score_type == 'pvalue':
            peak_df['SCORE'] = peak_df['-log10(pvalue)']
            peak_df['SCORE2'] = peak_df['pileup']
    elif peak_type == 'peakzilla':
        peak_df['SUMMIT'] = peak_df['Summit'] - peak_df['START']
        if score_type == 'score':
            peak_df['SCORE'] = peak_df['FoldEnrichment']
            peak_df['SCORE2'] = peak_df['FDR']
        elif score_type == 'pvalue':
            peak_df['SCORE'] = peak_df['FDR']
            peak_df['SCORE2'] = peak_df['FoldEnrichment']

    peak_df['#CHR'] = peak_df['#CHROM'].apply(lambda x: 'chr' + str(x))
    peak_df = peak_df[peak_df.apply(check_row, axis=1)]
    sorted_df = peak_df.sort_values(['SCORE', 'SCORE2'], ascending=False).reset_index(drop=True)
    tr_1 = sorted_df['SCORE'][min(len(peak_df.index) - 1, 999)]
    tr_2 = sorted_df['SCORE2'][min(len(peak_df.index) - 1, 999)]
    peak_df_trunc = peak_df[(peak_df['SCORE'] > tr_1) | ((peak_df['SCORE'] == tr_1) & (peak_df['SCORE2'] >= tr_2))]
    if peak_df.empty:
        print('empty peaks, {}'.format(peak_file_name))
        exit(1)
    peak_df_trunc[['#CHR', 'START', 'END', 'SUMMIT']].to_csv(out_path, sep='\t', index=False)


if __name__ == '__main__':
    main(peak_file_name=os.path.expanduser(sys.argv[1]), peak_type=sys.argv[2], score_type=sys.argv[3], out_path=os.path.expanduser(sys.argv[4]))

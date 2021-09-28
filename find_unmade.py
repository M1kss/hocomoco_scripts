import json
import pandas as pd
import os

# FIXME
def get_unique(x, columns):
    return '@'.join([x[columns[2]], x[columns[3]], x[columns[4]], x[columns[5]]])


def main():
    with open(os.path.expanduser('~/info.json')) as js:
        d = json.load(js)
    df = pd.read_csv('~/hoco-master-human.tsv', header=None)
    df['unique'] = df.apply(lambda x: get_unique(x, df.columns), axis=1)
    known_tfs = pd.read_excel('~/hocomoco.xlsx', engine='openpyxl')
    good_exps = known_tfs['curated:uniprot_ac'].unique()
    exps = set(d.keys()).intersection(good_exps)
    print(len(exps), sum([len([y for y in d[x] if y['diag'] and y['diag'][0] == 'Unexpected interrupt']) for x in exps]))
    df['ident'] = df[df.columns[1]].isin(exps)
    df = df.sort_values('ident', ascending=False)
    print(df)
    int_exps = []
    for tf, array in d.items():
        for item in array:
            if item['diag'] and item['diag'][0] == 'Unexpected interrupt':
                int_exps.append('@'.join(
                    [
                        item['name'],
                        item['caller'],
                        item['selected_by'],
                        item['motif_type']
                    ]))
    df2 = df[df['unique'].isin(int_exps)]

    df2[df2.columns[:-2]].to_csv('~/new-hoco.csv', header=None, index=None)


main()

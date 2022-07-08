import pandas as pd
import xlsxwriter
import json
import os
from base64 import b64encode
from drawlogo import start
import requests
from cairosvg import svg2png
from tqdm import tqdm
import sys
import multiprocessing as mp
from cor import dict_types, motif_dir, result_path, read_info_dict, read_cisbp_df, allowed_tfs, \
    hocomoco_path


def get_made_part(objs, index, parts=10):
    div, mod = divmod(index, (len(objs) // parts))
    if mod == 0:
        return True, div
    else:
        return False, None


def get_image_code(svg):
    if svg is None:
        return None
    elif svg.startswith('http'):
        r = requests.get(svg)
        result = r.content
    else:
        with open(svg, 'rb') as svg_image:
            result = svg_image.read()
    return 'data:image/png;base64,' + b64encode(result).decode('ascii')


def draw_svg(pcm_path, revcomp):
    directory = os.path.expanduser('~/svgs')
    if not os.path.isdir(directory):
        os.mkdir(directory)
    out_path = os.path.join(directory, os.path.basename(pcm_path))
    try:
        start.draw_logo(pcm_path,
                        revcomp=revcomp,
                        out_path=out_path,
                        unit_height=80,
                        unit_width=40)
    except Exception:
        print(out_path, pcm_path)
        raise
    svg2png(url=out_path, write_to=out_path, output_height=100, dpi=5)

    return out_path


def craft_motif_name(exp):
    return '.'.join(map(str,
                        [
                            exp['name'],
                            exp['selected_by'].replace('-', ''),
                            exp['caller'],
                            exp['motif_index']
                        ]))


def get_comp_motif_path(motif_name, d_type=None):
    if d_type == 'hocomoco':
        return os.path.join(hocomoco_path, motif_name + '.pcm')
    else:
        return os.path.join(motif_dir, motif_name + '.ppm')


def get_cisbp_tf(motif_name, cisbp_dict, d_type=None):
    if d_type == 'hocomoco':
        return '.'.join(motif_name.split('.')[-2:])
    else:
        return cisbp_dict.get(os.path.splitext(motif_name)[0])


def get_format(param, green_format, yellow_format, null_format):
    if param >= 0.1:
        return green_format
    elif param >= 0.05:
        return yellow_format
    else:
        return null_format


def get_max(exp):
    try:
        return max([(x, exp[x]['sim']) for x in exp if x in dict_types and exp[x]['sim']],
                   key=lambda x: x[1])
    except ValueError:
        return None, 0


def write_tf(report_path, sorted_tf_info):
    workbook = xlsxwriter.Workbook(report_path)
    print(report_path)
    green_format = workbook.add_format({'bg_color': '#C6EFCE'})
    yellow_format = workbook.add_format({'bg_color': '#FFF77D'})
    null_format = workbook.add_format()
    sheet = workbook.add_worksheet()
    try:
        name_width = len(max([exp['name'] for exp in sorted_tf_info]))
    except ValueError:
        name_width = 1
    try:
        motif_len = max([exp['motif_len'] for exp in sorted_tf_info])
    except ValueError:
        motif_len = 1
    sheet.write(0, 0, 'Name')
    sheet.write(0, 1, 'Specie')
    sheet.write(0, 2, 'Motif type')
    sheet.write(0, 3, 'Words')
    sheet.write(0, 4, 'Seqs.fraction')
    sheet.write(0, 5, 'Motif')
    sheet.write(0, 6, 'HOCOMOCO_sim')
    sheet.write(0, 7, 'HOCOMOCO_info')
    for index, d_type in enumerate(dict_types[1:]):
        sheet.write(0, 8 + index, d_type + '_sim')
    sheet.write(0, 8 + len(dict_types[1:]), 'Most_sim_motif')
    sheet.write(0, 9 + len(dict_types[1:]), 'Most_sim_TF')
    sheet.write(0, 10 + len(dict_types[1:]), 'Most_sim_type')
    sheet.freeze_panes(1, 0)  # Freeze the first row. KDIC
    for index, exp in tqdm(enumerate(sorted_tf_info), total=len(sorted_tf_info)):
        sheet.set_column(0, 0, name_width)
        sheet.set_column(1, 2, 1.5)
        sheet.set_column(5, 5, motif_len * 2.5)
        sheet.write(index + 1, 0, exp['name'])
        sheet.write(index + 1, 1, exp['specie'][0].upper())
        sheet.write(index + 1, 2, exp['selected_by'][:1].capitalize())
        sheet.write(index + 1, 3, exp['words'])
        sheet.write(index + 1, 4, round(exp['seqs'] / exp['total'], 2))
        sheet.set_row(index + 1, 30)

        for i, d_type in enumerate(dict_types[1:]):
            sheet.write(index + 1, 8 + i, round(exp[d_type]['sim'], 2) if exp[d_type]['sim'] else None)
        best_d_type, best_sim = get_max(exp)
        if exp['hocomoco']['sim']:
            hocomoco_orient = exp['hocomoco']['orientation'] == 'revcomp'
            sheet.write(index + 1, 6, round(exp['hocomoco']['sim'], 2),
                        get_format(exp['hocomoco']['sim'], green_format, yellow_format, null_format))
            sheet.write(index + 1, 7, exp['hocomoco']['name'])
            sheet.insert_image(index + 1, 5,
                               draw_svg(exp['pcm_path'], hocomoco_orient),
                               {'x_scale': 0.4, 'y_scale': 0.4})
            best_sim_motif = draw_svg(get_comp_motif_path(exp[best_d_type]['motif'],
                                                          best_d_type),
                                      hocomoco_orient ^ (exp[best_d_type]['orientation'] == 'revcomp'))
        else:
            sheet.insert_image(index + 1, 5,
                               draw_svg(exp['pcm_path'], exp[best_d_type]['orientation'] == 'revcomp'),
                               {'x_scale': 0.4, 'y_scale': 0.4})
            best_sim_motif = draw_svg(get_comp_motif_path(exp[best_d_type]['motif'],
                                                          best_d_type),
                                      False)

        sheet.insert_image(index + 1, 8 + len(dict_types[1:]), best_sim_motif, {'x_scale': 0.4, 'y_scale': 0.4})
        sheet.set_column(8 + len(dict_types[1:]), 8 + len(dict_types[1:]), motif_len * 2.5)
        sheet.write(index + 1, 9 + len(dict_types[1:]), exp[best_d_type]['name'])
        sheet.write(index + 1, 10 + len(dict_types[1:]), best_d_type)
    workbook.close()


def process_tf(tf_name, tf_info, cisbp_dict):
    if allowed_tfs is not None:
        if tf_name in allowed_tfs:
            return
    print('Processing {}'.format(tf_name))

    sim_dict = {}
    for d_type in dict_types:
        name = os.path.join(result_path, f'{tf_name}@{d_type}.json')
        if not os.path.exists(name):
            print(name)
            continue
        with open(name) as f:
            sim_dict[d_type] = json.load(f)
    # if os.path.exists(os.path.join('reports', tf_name + '.1.xlsx')):
    #     return

    print('Parsing sim dict')
    for exp in tqdm(tf_info):
        exp['name'] = craft_motif_name(exp)
        pcm_name = os.path.splitext(os.path.basename(exp['pcm_path']))[0]
        for i, d_type in enumerate(dict_types):
            motifs = sim_dict.get(d_type)
            if not motifs:
                exp[d_type] = {'motif': None, 'sim': None, 'name': ''}
                continue

            comp = motifs.get(pcm_name)
            if not comp:
                exp[d_type] = {'motif': None, 'sim': None, 'name': ''}
                continue
            tf_cisbp_name = get_cisbp_tf(comp['motif'], cisbp_dict, d_type)
            exp[d_type] = {'motif': comp['motif'].replace('.txt', ''),  # FIXME
                           'orientation': comp['orientation'],
                           'sim': float(comp['similarity']),
                           'name': tf_cisbp_name}
    if len(tf_info) > 0 and tf_info[0]['hocomoco']['sim']:
        tf_info = sorted(tf_info, key=lambda x: x['hocomoco']['sim'], reverse=True)
        tf_info = sorted(tf_info, key=lambda x: x['hocomoco']['name'])
    sorted_tf_info = [x for x in tf_info if get_max(x)[1] >= 0.01]
    chunk_size = 1000
    parts_start = [i for i in range(0, len(sorted_tf_info), chunk_size)]
    for i in parts_start:
        write_tf(os.path.join('reports', '{}.{}.xlsx'.format(tf_name, i // chunk_size + 1)),
                 sorted_tf_info[i:min(i + chunk_size, len(sorted_tf_info))])


def main(njobs=1):
    info_dict = read_info_dict()
    cisbp_dfs = read_cisbp_df()
    cisbp_dict = {}
    print('Reading CIS-BP')
    for key, value in cisbp_dfs.items():
        df = value[value['TF_Status'] == 'D']
        df['TF_Name'] = df['TF_Name'].apply(lambda x: x.upper() + '_{}'.format(key.upper()))
        cisbp_dict = {**cisbp_dict,
                      **pd.Series(df['TF_Name'].values, index=df.Motif_ID).to_dict()}
    if njobs > 1:
        ctx = mp.get_context("forkserver")
        with ctx.Pool(njobs) as p:
            p.starmap(process_tf, [(tf_name, tf_info, cisbp_dict) for tf_name, tf_info in info_dict.items()])
    else:
        for tf_name, tf_info in info_dict.items():
            process_tf(tf_name, tf_info, cisbp_dict)


if __name__ == '__main__':
    main(int(sys.argv[1]))

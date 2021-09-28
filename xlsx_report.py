import xlsxwriter
import json
import os
import sys
from base64 import b64encode
from drawlogo import start
import requests
from cairosvg import svg2png
import pandas as pd
from cor import dict_types, motif_dir, result_path, cisbp_dict_path, allowed_tfs, filter_pwms, read_dicts


if os.path.exists(cisbp_dict_path):
    df = pd.read_table(cisbp_dict_path)
    df = df[df['TF_Status'] == 'D']
    cisbp_dict = pd.Series(df.TF_Name.values, index=df.Motif_ID).to_dict()


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
    out_path = os.path.join(directory, os.path.basename(pcm_path))
    if not os.path.isdir(directory):
        os.mkdir(directory)
    start.draw_logo(pcm_path,
                    revcomp=revcomp,
                    out_path=out_path,
                    unit_height=80,
                    unit_width=40)
    svg2png(url=out_path, write_to=out_path, output_height='20', dpi=5)

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
        return os.path.join('pcm', motif_name + '.pcm')
    else:
        return os.path.join(motif_dir, motif_name + '.ppm')


def get_cisbp_tf(motif_name, d_type=None):
    if d_type == 'hocomoco':
        return '.'.join(motif_name.split('.')[-2:])
    else:
        return cisbp_dict.get(motif_name)


def get_image_code_for_json(tf_info, t_factor):
    with open(os.path.join(result_path, t_factor + '.json')) as f:
        sim_dict = json.loads(f.readline())
    similar_motifs = set()
    tf_images = {}
    for index, exp in enumerate(tf_info):
        exp['name'] = craft_motif_name(exp)
        if index % 100 == 0:
            print('Done {} motifs for {}'.format(index, t_factor))
        if exp.get('motif_image') is None:
            exp['motif_image'] = draw_svg(exp['pcm_path'], False)
        exp['motif_image'] = get_image_code(exp['motif_image'])
        pcm_name = os.path.splitext(os.path.basename(exp['pcm_path']))[0]
        for d_type in dict_types:
            motifs = sim_dict.get(d_type)
            if not motifs:
                print('No {} motifs for {}'.format(d_type, tf))
                exp[d_type] = {'motif': None, 'sim': None, 'name': None}
                continue
            comp = motifs.get(pcm_name)
            if not comp:
                print('No {} comp for {}. {}'.format(d_type, tf, pcm_name))
                exp[d_type] = {'motif': None, 'sim': None, 'name': None}
                continue
            similar_motifs.add((comp['motif'], comp['orientation']))
    print('Drawing cisbp')
    for index, (motif, orient) in enumerate(similar_motifs):
        to_print, part = get_made_part(similar_motifs, index, parts=10)
        if to_print:
            print('Done {} part of 10'.format(part))
        try:
            tf_images[motif] = get_image_code(
                draw_svg(get_comp_motif_path(motif),
                         revcomp=True if orient == 'revcomp' else False))
        except TypeError:
            print(motif)
            raise
    for index, exp in enumerate(tf_info):
        pcm_name = os.path.splitext(os.path.basename(exp['pcm_path']))[0]
        for d_type in dict_types:
            motifs = sim_dict.get(d_type)
            if not motifs:
                print('No {} motifs for {}'.format(d_type, tf))
                exp[d_type] = {'motif': None, 'sim': None, 'name': None}
                continue
            comp = motifs.get(pcm_name)
            if not comp:
                print('No {} comp for {}. {}'.format(d_type, tf, pcm_name))
                exp[d_type] = {'motif': None, 'sim': None, 'name': None}
                continue
            tf_cisbp_name = get_cisbp_tf(comp['motif'], d_type)

            exp[d_type] = {'motif': tf_images.get(comp['motif']),
                           'sim': round(float(comp['similarity']), 2),
                           'name': tf_cisbp_name
                           }


def get_format(param):
    if param >= 0.1:
        return green_format
    elif param >= 0.05:
        return yellow_format
    else:
        return null_format


def process_tf(sheet, t_factor, tf_info):
    if not os.path.exists(os.path.join(result_path, t_factor + '.json')):
        return
    with open(os.path.join(result_path, t_factor + '.json')) as f:
        sim_dict = json.loads(f.readline())
    for index, exp in enumerate(tf_info):
        exp['name'] = craft_motif_name(exp)
        exp['motif_image'] = draw_svg(exp['pcm_path'], False)
        pcm_name = os.path.splitext(os.path.basename(exp['pcm_path']))[0]
        for i, d_type in enumerate(dict_types):
            motifs = sim_dict.get(d_type)
            if not motifs:
                print('No {} motifs for {}'.format(d_type, tf))
                exp[d_type] = {'motif': None, 'sim': None, 'name': ''}
                continue
            comp = motifs.get(pcm_name)
            if not comp:
                print('No {} comp for {}. {}'.format(d_type, tf, pcm_name))
                exp[d_type] = {'motif': None, 'sim': None, 'name': ''}
                continue
            tf_cisbp_name = get_cisbp_tf(comp['motif'], d_type)
            exp[d_type] = {'motif': comp['motif'],
                           'orientation': comp['orientation'],
                           'sim': float(comp['similarity']),
                           'name': tf_cisbp_name}
    sorted_tf_info = sorted(tf_info, key=lambda x: x['hocomoco']['sim'], reverse=True)
    sorted_tf_info = sorted(sorted_tf_info, key=lambda x: x['hocomoco']['name'], reverse=True)

    try:
        name_width = len(max([exp['name'] for exp in sorted_tf_info]))
    except ValueError:
        name_width = 1
    try:
        motif_len = max([exp['motif_len'] for exp in sorted_tf_info])
    except ValueError:
        motif_len = 1
    sheet.write(0, 0, 'Name')
    sheet.write(0, 1, 'Motif type')
    sheet.write(0, 2, 'Words')
    sheet.write(0, 3, 'Seqs.fraction')
    sheet.write(0, 4, 'Motif')
    sheet.write(0, 5, 'HOCOMOCO_sim')
    sheet.write(0, 6, 'HOCOMOCO_info')
    for index, d_type in enumerate(dict_types[1:]):
        sheet.write(0, index + 7, d_type + '_sim')
    sheet.write(0, 7 + len(dict_types[1:]), 'Most_sim_motif')
    sheet.write(0, 8 + len(dict_types[1:]), 'Most_sim_TF')
    sheet.write(0, 9 + len(dict_types[1:]), 'Most_sim_type')
    worksheet.freeze_panes(1, 0)  # Freeze the first row. KDIC
    for index, exp in enumerate(sorted_tf_info):
        sheet.set_column(0, 0, name_width)
        sheet.set_column(4, 4, motif_len * 2.5)
        sheet.write(index + 1, 0, exp['name'])
        sheet.write(index + 1, 1, exp['selected_by'][:1].capitalize())
        sheet.write(index + 1, 2, exp['words'])
        sheet.write(index + 1, 3, exp['seqs']/exp['total'])
        sheet.insert_image(index + 1, 4, exp['motif_image'], {'x_scale': 0.4, 'y_scale': 0.4})
        sheet.set_row(index, 30)
        sheet.write(index + 1, 5, exp['hocomoco']['sim'], get_format(exp['hocomoco']['sim']))
        sheet.write(index + 1, 6, exp['hocomoco']['name'])
        for i, d_type in enumerate(dict_types[1:]):
            sheet.write(index + 1, i + 7, exp[d_type]['sim'])
        best_d_type, _ = max([(x, exp[x]['sim']) for x in exp if x in dict_types and exp[x]['sim']],
                             key=lambda x: x[1])
        best_sim_motif = draw_svg(get_comp_motif_path(exp[best_d_type]['motif'], best_d_type),
                                  revcomp=True if exp[best_d_type]['orientation'] == 'revcomp' else False)
        sheet.insert_image(index + 1, 7 + len(dict_types[1:]), best_sim_motif, {'x_scale': 0.4, 'y_scale': 0.4})
        sheet.set_column(7 + len(dict_types[1:]), 7 + len(dict_types[1:]), motif_len * 2.5)
        sheet.write(index + 1, 8 + len(dict_types[1:]), exp[best_d_type]['name'])
        sheet.write(index + 1, 9 + len(dict_types[1:]), best_d_type)


if __name__ == '__main__':
    tfs_stats = sys.argv[1] if len(sys.argv) > 1 else None
    hocomoco_dict = read_dicts()['hocomoco']
    if tfs_stats is not None:
        with open(tfs_stats) as opened_json:
            d = json.loads(opened_json.readline())
            for tf in hocomoco_dict:
                tf_name = tf + '_HUMAN'
                report_path = os.path.join('reports', tf_name + '.xlsx')
                if os.path.exists(report_path):
                    continue
                if tf_name in d:
                    print('Now doing', tf_name)
                    workbook = xlsxwriter.Workbook(report_path)
                    green_format = workbook.add_format({'bg_color': '#C6EFCE'})
                    yellow_format = workbook.add_format({'bg_color': '#FFF77D'})
                    null_format = workbook.add_format()
                    worksheet = workbook.add_worksheet()
                    process_tf(worksheet, tf_name, filter_pwms(d[tf_name]))
                    workbook.close()

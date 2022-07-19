"""
Usage:
    script.py [options] -d database -f figure_folder --df figure_dest_file --ds subfiture_dest_file

Options:
    -d <file>           Database file
    -f <directory>      Figure folder
    --df <file>         Figure dest file
    --ds <file>         Subfigure dest file
"""

import collections
import datetime
import json
import sqlite3
from pathlib import Path
from typing import List

import docopt
import tqdm
from PIL import Image

from figurex_db.db_utils import DBHelper, select_helper
from figurex_db.sqlite_stmt import sql_select_empty_subfigurejsonfiles, sql_insert_subfigure, sql_select_subfigure, \
    sql_update_has_subfigure1, sql_update_has_subfigure0, sql_select_figure
from figurex.commons import generate_path
import pandas as pd

Subfigure = collections.namedtuple('Subfigure', 'subfigure_name xtl ytl xbr ybr')


def split_subfigure(figure_file) -> List[Subfigure]:
    subfigure_json_file = figure_file.with_suffix('.json')
    if not subfigure_json_file.exists():
        return []

    with open(subfigure_json_file) as fp:
        subfigures = json.load(fp)

    if len(subfigures) <= 1:
        return []

    records = []
    im = Image.open(figure_file)
    for subfigure in subfigures:
        xtl = subfigure['x']
        ytl = subfigure['y']
        xbr = xtl + subfigure['w']
        ybr = ytl + subfigure['h']
        dst = figure_file.parent / f'{figure_file.stem}_{xtl}x{ytl}_{xbr}x{ybr}{figure_file.suffix}'
        if not dst.exists():
            subim = im.crop((xtl, ytl, xbr, ybr))
            subim.save(dst)
        records.append(Subfigure(dst.name, xtl, ytl, xbr, ybr))
    return records


def get_subfigure_f(db_file, image_dir, subfigures_dst):
    conn = sqlite3.connect(db_file)

    df = select_helper(conn, sql_select_empty_subfigurejsonfiles, ['pmcid', 'figure_name'])

    insert_time = f'{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}'
    insert_subfigure_helper = DBHelper(conn, sql_insert_subfigure)
    insert_subfigure_helper.start()
    for pmcid, figure_name in tqdm.tqdm(zip(df['pmcid'], df['figure_name']), total=len(df),
                                        desc='Query new subfigures'):
        figure_file = image_dir / generate_path(pmcid) / '{}_{}'.format(pmcid, figure_name)
        records = split_subfigure(figure_file)
        records_to_insert = [(pmcid, figure_name, r.xtl, r.ytl, r.xbr, r.ybr, 'PMCFigureX', insert_time)
                             for r in records]
        insert_subfigure_helper.extend(records_to_insert)
    insert_subfigure_helper.finish()
    insert_subfigure_helper.summarize()

    # get all subfigures
    df = select_helper(conn, sql_select_subfigure, ['pmcid', 'figure_name', 'xtl', 'ytl', 'xbr', 'ybr'])
    data = []
    for i, row in tqdm.tqdm(df.iterrows(), total=len(df), desc='Get subfigures'):
        pmcid = row['pmcid']
        figure_name = row['figure_name']
        xtl = row['xtl']
        ytl = row['ytl']
        xbr = row['xbr']
        ybr = row['ybr']
        figure_file = generate_path(pmcid) / '{}_{}'.format(pmcid, figure_name)
        dst = figure_file.parent / f'{figure_file.stem}_{xtl}x{ytl}_{xbr}x{ybr}{figure_file.suffix}'
        data.append({'pmcid': pmcid,
                     'figure path': str(dst.as_posix()),
                     'xtl': xtl,
                     'ytl': ytl,
                     'xbr': xbr,
                     'ybr': ybr,
                     'type': 'subfigure'})
    df = pd.DataFrame(data)
    df.to_csv(subfigures_dst, index=False)
    conn.close()


def get_figure_f(db_file, image_dir, figures_dst):
    conn = sqlite3.connect(db_file)
    df = select_helper(conn, sql_select_figure, ['pmcid', 'figure_name', 'width', 'height'])
    data = []
    for i, row in tqdm.tqdm(df.iterrows(), total=len(df), desc='Get whole figures'):
        pmcid = row['pmcid']
        figure_name = row['figure_name']
        figure_file = generate_path(pmcid) / '{}_{}'.format(pmcid, figure_name)
        data.append({'pmcid': pmcid,
                     'figure path': str(figure_file.as_posix()),
                     'xtl': 0,
                     'ytl': 0,
                     'xbr': row['width'],
                     'ybr': row['height'],
                     'type': 'figure'})

    df = pd.DataFrame(data)
    df.to_csv(figures_dst, index=False)
    conn.close()


def update_has_subfigure(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(sql_update_has_subfigure0)
    c.execute(sql_update_has_subfigure1)
    conn.commit()


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    db_file = args['-d']
    image_dir = Path(args['-f'])
    get_subfigure_f(db_file=db_file, image_dir=image_dir, subfigures_dst=args['--ds'])
    get_figure_f(db_file=db_file, image_dir=image_dir, figures_dst=args['--df'])

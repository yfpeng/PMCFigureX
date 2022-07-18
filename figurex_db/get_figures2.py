"""
Usage:
    script.py [options] -d database -f figure_folder

Options:
    -d <file>           Database file
    -f <directory>      Figure folder
"""

import collections
import re
import sqlite3
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

import docopt
import requests
import tqdm
from PIL import Image

from figurex_db import ppprint
from figurex_db.db_utils import select_helper, DBHelper
from figurex_db.sqlite_stmt import sql_get_empty_figures, sql_update_figure_size
from figurex_db.utils import generate_path


def get_taz_file(pmcid, local_tgz_file, error_handler=True):
    try:
        url = f'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}'
        response = requests.get(url)
        m = re.search(r'ftp:.*.gz', response.text)
        if m:
            ftp_url = m.group()
            try:
                urllib.request.urlretrieve(ftp_url, local_tgz_file)
            except urllib.error.HTTPError:
                if error_handler:
                    with open(local_tgz_file, 'w') as _:
                        pass
    except Exception as e:
        print(e)


def get_figures(db_file, image_dir):
    conn = sqlite3.connect(db_file)

    df = select_helper(conn, sql_get_empty_figures, ['pmcid', 'figure_name'])

    cnt = collections.Counter()
    update_figure_helper = DBHelper(conn, sql_update_figure_size)
    update_figure_helper.start()
    for pmcid, figure_name in tqdm.tqdm(zip(df['pmcid'], df['figure_name']), total=len(df)):
        local_tgz_file = image_dir / generate_path(pmcid) / f'{pmcid}.tar.gz'
        # local_tgz_file.parent.mkdir(parents=True, exist_ok=True)

        local_file = image_dir / generate_path(pmcid) / '{}_{}'.format(pmcid, figure_name)
        if not local_file.exists():
            if not local_tgz_file.exists():
                get_taz_file(pmcid, local_tgz_file, True)
            try:
                t = tarfile.open(local_tgz_file, 'r')
                for member in t.getmembers():
                    if member.name == f'{pmcid}/{figure_name}':
                        r = t.extractfile(member)
                        with open(local_file, 'wb') as fp:
                            fp.write(r.read())
            except Exception as e:
                cnt['Http error'] += 1
                with open(local_file, 'w') as _:
                    pass

        try:
            im = Image.open(local_file)
            update_figure_helper.append((im.width, im.height, pmcid, figure_name))
        except:
            cnt['Image error'] += 1
        cnt['total figure'] += 1

    update_figure_helper.finish()
    conn.close()

    ppprint.pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figures(args['-d'], Path(args['-f']))

"""
Usage:
    script.py [options] -d database -f figure_folder

Options:
    -d <file>           Database file
    -f <directory>      Figure folder
"""

import collections
import sqlite3
import urllib.error
import urllib.request
from pathlib import Path

import docopt
import tqdm
from PIL import Image

from figurex_db import ppprint
from figurex_db.db_utils import select_helper, DBHelper
from figurex_db.sqlite_stmt import sql_get_empty_figures, sql_update_figure_size
from figurex.commons import generate_path


def get_figures(db_file, image_dir):
    conn = sqlite3.connect(db_file)

    df = select_helper(conn, sql_get_empty_figures, ['pmcid', 'figure_name'])

    cnt = collections.Counter()
    update_figure_helper = DBHelper(conn, sql_update_figure_size)
    update_figure_helper.start()
    for pmcid, figure_name in tqdm.tqdm(zip(df['pmcid'], df['figure_name']), total=len(df)):
        local_file = image_dir / generate_path(pmcid) / '{}_{}'.format(pmcid, figure_name)
        if not local_file.exists():
            try:
                url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/bin/{figure_name}'
                urllib.request.urlretrieve(url, local_file)
                cnt['new figure'] += 1
            except urllib.error.HTTPError:
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

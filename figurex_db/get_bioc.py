"""
Usage:
    script.py [options] -d database -b bioc_folder

Options:
    -d <file>           Database file
    -b <directory>      BioC folder
"""

import collections
import sqlite3
import urllib.error
import urllib.request
from pathlib import Path

import docopt
import tqdm

from figurex_db.db_utils import DBHelper, select_helper
from figurex_db.sqlite_stmt import sql_select_empty_bioc, sql_update_articles
from figurex_db.utils import generate_path


def get_bioc(pmid, dest):
    url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmid}/unicode'
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, 'w', encoding='utf8') as fp:
        fp.write(text)


def get_bioc_f(db_file, bioc_dir):
    conn = sqlite3.connect(db_file)
    df = select_helper(conn, sql_select_empty_bioc, ['pmcid', 'pmid'])
    #
    cnt = collections.Counter()
    update_article_helper = DBHelper(conn, sql_update_articles)
    update_article_helper.start()
    for pmcid, pmid in tqdm.tqdm(zip(df['pmcid'], df['pmid']), total=len(df)):
        cnt['total pmc'] += 1
        dst_dir = bioc_dir / generate_path(pmcid)
        dst = dst_dir / f'{pmcid}.xml'
        if dst.exists():
            update_article_helper.append((1, pmcid))
        else:
            try:
                get_bioc(pmid, dst)
                cnt['new bioc'] += 1
                update_article_helper.append((1, pmcid))
            except urllib.error.HTTPError:
                update_article_helper.append((0, pmcid))

    update_article_helper.finish()
    conn.close()

    for k, v in cnt.most_common():
        print(k, ':', v)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_bioc_f(args['-d'], Path(args['-b']))

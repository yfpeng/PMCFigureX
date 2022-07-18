"""
Usage:
    script.py [options] -d database -l litcovid_file

Options:
    -d <file>       Database file
    -l <file>       LitCovid file
"""

import datetime
import io
import os
import sqlite3
from pathlib import Path
from typing import List, Dict

import docopt
import pandas as pd
import requests
import tqdm

from figurex_db.db_utils import select_helper, DBHelper
from figurex_db.sqlite_stmt import sql_insert_articles, sql_select_articles


def get_pmc_from_pmid(pmids: List[str]) -> Dict:
    assert len(pmids) <= 200
    url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&format=csv&email=fake@fake.com&ids='
    url += ','.join(pmids)
    x = requests.get(url)
    f = io.StringIO(x.text.strip())
    pmcdf = pd.read_csv(f, dtype=str)

    rst = {}
    for pmid, pmcid, doi in zip(pmcdf['PMID'], pmcdf['PMCID'], pmcdf['DOI']):
        if not pd.isna(pmcid):
            rst[pmid] = {'pmcid': pmcid, 'doi': doi}
    return rst


def get_pmc_from_pmid_f(src, db_file):
    pubmed_export_df = pd.read_csv(src, sep='\t', dtype=str, comment='#')

    new_pmids = set(pubmed_export_df['pmid'])
    conn = sqlite3.connect(os.path.expanduser(db_file))

    history_df = select_helper(conn, sql_select_articles, columns=['pmid'])
    new_pmids = new_pmids - set(history_df['pmid'])

    insert_time = f'{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}'
    pmids = list(new_pmids)

    insert_articles_helper = DBHelper(conn, sql_insert_articles)
    insert_articles_helper.start()
    for i in tqdm.tqdm(range(0, len(pmids), 200)):
        results = get_pmc_from_pmid(pmids[i: i + 200])
        for pmid, v in results.items():
            insert_articles_helper.append((v['pmcid'], pmid, v['doi'], insert_time))

    insert_articles_helper.finish()
    conn.close()


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_pmc_from_pmid_f(Path(args['-l']), Path(args['-d']))

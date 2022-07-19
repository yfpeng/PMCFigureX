"""
Usage:
    script.py [options] -q STR -o DEST

Options:
    -q <str>        Query
    -o <file>       PMC file
"""

import datetime
from pathlib import Path
import docopt
import pandas as pd
from Bio import Entrez


def search(query, email='your.email@example.com', default_retmax=100):
    Entrez.email = email
    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmode='xml',
                            retmax=default_retmax,
                            term=query,
                            usehistory='y')
    record = Entrez.read(handle)
    total = int(record['Count'])
    retmax = int(record['RetMax'])
    retstart = int(record['RetStart'])
    webenv = record['RetStart']
    print('There are %s records' % total)
    print('Search %s-%s records' % (retstart, retstart + retmax))
    yield record['IdList']
    while retstart + retmax < total:
        retstart = retstart + retmax
        print('Search %s-%s records' % (retstart, retstart + retmax))
        handle = Entrez.esearch(db='pubmed',
                                sort='relevance',
                                retmode='xml',
                                retmax=default_retmax,
                                term=query,
                                usehistory='y',
                                retstart=retstart,
                                WebEnv=webenv)
        record = Entrez.read(handle)
        retmax = int(record['RetMax'])
        retstart = int(record['RetStart'])
        yield record['IdList']


def fetch_details(id_list, email='your.email@example.com'):
    ids = ','.join(id_list)
    Entrez.email = email
    handle = Entrez.esummary(db='pubmed',
                             retmode='xml',
                             id=ids)
    results = Entrez.read(handle)
    return results


def parse_results(results):
    data = []
    insert_time = f'{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}'
    for paper in results:
        has_pmc = 'pmc' in paper['ArticleIds']
        if has_pmc:
            x = {
                'pmid': paper['Id'],
                'pmcid': paper['ArticleIds']['pmc'],
                # 'doi': paper['DOI'],
                'title': paper['Title'],
                'journal': paper['Source'],
                'insert_time': insert_time
            }
            data.append(x)
    return data


def query_pubmed(query, dest):
    total_data = []
    for pubmids in search(query, default_retmax=1000):
        papers = fetch_details(pubmids)
        data = parse_results(papers)
        total_data += data
    df = pd.DataFrame(total_data)
    df = df.sort_values(by='pmid')
    df.to_csv(dest, index=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    query_pubmed(args['-q'], Path(args['-o']))

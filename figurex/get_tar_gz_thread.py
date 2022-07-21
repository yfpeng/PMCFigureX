"""
Usage:
    script.py [options] -i SOURCE -a FILE -o DEST -f FIGURE_DIR

Options:
    -i <file>   CSV file with pmcid
    -a <file>   OA file list
    -o <file>   CSV file with a new "has_targz" field
    -f <dir>    Figure folder
"""
import concurrent
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from figurex import ppprint
from figurex.commons import generate_path

import collections

from pathlib import Path

import docopt
import pandas as pd
import tqdm
from ftplib import FTP


def download_taz_file(ftp_url, dest):
    try:
        url = 'https://ftp.ncbi.nlm.nih.gov/pub/pmc/{}'.format(ftp_url)
        urllib.request.urlretrieve(url, dest)
        return True
    except:
        return False

    # with FTP('ftp.ncbi.nlm.nih.gov') as ftp:
    #     ftp.login()
    #     ftp.cwd('pub/pmc')
    #     try:
    #         with open(dest, 'wb') as fp:
    #             ftp.retrbinary("RETR " + ftp_url, fp.write)
    #         return True
    #     except Exception as e:
    #         print(e)
    #         return False


def get_taz_file(src, dest, oa_file_list, output_dir):
    print('Load oa file list')
    oa_file_df = pd.read_csv(oa_file_list)
    print('Done')

    df = pd.read_csv(src, dtype=str)

    pmcids = set(df['pmcid'])
    oa_file_df_sub = oa_file_df.loc[oa_file_df['Accession ID'].isin(pmcids)]

    cnt = collections.Counter()

    cnt['Total PMC'] = len(pmcids)
    cnt['Total tar.gz'] = 0
    cnt['New tar.gz'] = 0
    cnt['Failed tar.gz'] = 0

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for _, row in tqdm.tqdm(oa_file_df_sub.iterrows(), total=len(oa_file_df_sub)):
            pmcid = row['Accession ID']
            local_tgz_file = output_dir / generate_path(pmcid) / f'{pmcid}.tar.gz'
            if not local_tgz_file.exists():
                local_tgz_file.parent.mkdir(parents=True, exist_ok=True)
                futures.append(executor.submit(download_taz_file, ftp_url=row['File'], dest=local_tgz_file))
            cnt['Total tar.gz'] += 1

        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            if future.result():
                cnt['New tar.gz'] += 1
            else:
                cnt['Failed tar.gz'] = +1

    has_targz = []
    for _, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        pmcid = row['pmcid']
        local_tgz_file = output_dir / generate_path(pmcid) / f'{pmcid}.tar.gz'
        if local_tgz_file.exists():
            has_targz.append(True)
        else:
            has_targz.append(False)

    df['has_targz'] = has_targz
    df.to_csv(dest, index=False)

    ppprint.pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_taz_file(src=Path(args['-i']),
                 dest=Path(args['-o']),
                 oa_file_list=Path(args['-a']),
                 output_dir=Path(args['-f']))


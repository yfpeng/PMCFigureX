"""
Usage:
    script.py [options] -i SOURCE -o FILE -f FIGURE_DIR

Options:
    -i <file>   Figure csv file
    -o <file>   OA file list
    -f <dir>    Figure folder
"""
from figurex import ppprint
from figurex.commons import generate_path

import collections

from pathlib import Path

import docopt
import pandas as pd
import tqdm
from ftplib import FTP


def get_taz_file(src, oa_file_list, image_dir):
    print('Load oa file list')
    oa_file_df = pd.read_csv(oa_file_list)
    print('Done')

    figure_df = pd.read_csv(src)

    pmcids = set(figure_df['pmcid'])
    oa_file_df_sub = oa_file_df.loc[oa_file_df['Accession ID'].isin(pmcids)]

    cnt = collections.Counter()

    cnt['Total PMC'] = len(pmcids)
    cnt['Total tar.gz'] = 0
    cnt['New tar.gz'] = 0

    ftp = FTP('ftp.ncbi.nlm.nih.gov')
    ftp.login()
    ftp.cwd('pub/pmc')
    for _, row in tqdm.tqdm(oa_file_df_sub.iterrows(), total=len(oa_file_df_sub)):
        pmcid = row['Accession ID']
        local_tgz_file = image_dir / generate_path(pmcid) / f'{pmcid}.tar.gz'
        if not local_tgz_file.exists():
            with open(local_tgz_file, 'wb') as fp:
                ftp.retrbinary("RETR " + row['File'], fp.write)
            cnt['New tar.gz'] += 1
        cnt['Total tar.gz'] += 1

    ppprint.pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_taz_file(src=Path(args['-i']),
                oa_file_list=Path(args['-o']),
                image_dir=Path(args['-f']))


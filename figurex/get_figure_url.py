"""
Usage:
    script.py [options] -i SOURCE -o DEST -b BIOC_DIR

Options:
    -i <file>       PMC csv file
    -o <file>       Total figure csv file
    -b <dir>        BioC folder
    --overwrite
"""

import collections
import datetime
from pathlib import Path

import bioc
import docopt
import pandas as pd
import tqdm

from figurex import ppprint
from figurex.commons import get_figure_link, generate_path, is_file_empty


def get_figure_caption(src, dest, bioc_dir, overwrite=False):
    if dest.exists() and not overwrite:
        print('%s will not be overwritten' % dest.name)
        return

    df = pd.read_csv(src, dtype=str)

    cnt = collections.Counter()

    cnt['Total PMC'] = len(df)
    cnt['Empty BioC'] = 0
    cnt['Ill-formatted BioC'] = 0
    cnt['Total figures'] = 0

    data = []
    insert_time = f'{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}'
    for pmcid in tqdm.tqdm(df['pmcid'], total=len(df)):
        biocfile = bioc_dir / generate_path(pmcid) / f'{pmcid}.xml'
        if is_file_empty(biocfile):
            cnt['Empty BioC'] += 1
            continue

        try:
            figures = get_figure_link(biocfile)
        except Exception as e:
            print(e)
            cnt['Ill-formatted BioC'] += 1
            continue

        for f in figures:
            data.append({
                'pmcid': pmcid,
                'figure_name': f,
                'insert_time': insert_time
            })

    df = pd.DataFrame(data)
    df = df.drop_duplicates()

    cnt['Total figures'] += len(df)

    df.to_csv(dest, index=False)

    ppprint.pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figure_caption(src=Path(args['-i']),
                       dest=Path(args['-o']),
                       bioc_dir=Path(args['-b']),
                       overwrite=args['--overwrite'])

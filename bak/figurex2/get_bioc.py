"""
Usage:
    script.py -i SOURCE -b DEST_DIR -o DEST

Options:
    -i <file>           CSV file with pmid and pmcid fields
    -o <file>           CSV file with a new "has_bioc" field
    -b <directory>      BioC folder
"""

import collections
import urllib.error
from pathlib import Path

import docopt
import pandas as pd
import tqdm

from figurex import ppprint
from figurex.commons import get_bioc, create_empty_file, generate_path, is_file_empty


def get_bioc_f(src, dest, bioc_dir):
    df = pd.read_csv(src, dtype=str)
    cnt = collections.Counter()

    cnt['Total PMC'] = len(df)
    cnt['Total BioC'] = 0
    cnt['Empty BioC'] = 0
    cnt['New   BioC'] = 0

    has_bioc = []
    for pmid, pmcid in tqdm.tqdm(zip(df['pmid'], df['pmcid']), total=len(df)):
        cnt['Total BioC'] += 1

        dst_dir = bioc_dir / generate_path(pmcid)
        dst = dst_dir / f'{pmcid}.xml'
        if dst.exists():
            if is_file_empty(dst):
                has_bioc.append(False)
                cnt['Empty BioC'] += 1
            else:
                has_bioc.append(True)
        else:
            try:
                get_bioc(pmid, dst)
                has_bioc.append(True)
                cnt['New BioC'] += 1
            except urllib.error.HTTPError:
                create_empty_file(dst)
                has_bioc.append(False)
                cnt['Empty BioC'] += 1

    df['has_bioc'] = has_bioc
    df.to_csv(dest, index=False)

    ppprint.pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_bioc_f(Path(args['-i']), Path(args['-o']), Path(args['-b']))

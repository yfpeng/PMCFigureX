"""
Usage:
    script.py [options] -i SOURCE -o DEST -f FIGURE_DIR

Options:
    -i <file>   CSV file with pmcid
    -o <file>   Figure CSV file
    -f <dir>    Figure folder
"""
import concurrent
import datetime
import tarfile
from concurrent.futures import ThreadPoolExecutor

from figurex import ppprint
from figurex.commons import generate_path

import collections
from pathlib import Path

import docopt
import pandas as pd
import tqdm


def extract_figures(local_tgz_file, image_dir, pmcid):
    data = []
    new_figures = 0
    try:
        with tarfile.open(local_tgz_file, 'r') as t:
            for member in t.getmembers():
                if member.name.endswith('.jpg'):
                    local_file = image_dir / generate_path(pmcid) / '{}'.format(member.name)
                    local_file.parent.mkdir(parents=True, exist_ok=True)
                    if not local_file.exists():
                        r = t.extractfile(member)
                        with open(local_file, 'wb') as fp:
                            fp.write(r.read())
                        new_figures += 1
                    data.append({
                        'pmcid': pmcid,
                        'figure_name': local_file.name,
                    })
    except Exception as e:
        print('%s: %s' % (pmcid, e))
    return data, new_figures


def get_figures(src, dest, image_dir):
    df = pd.read_csv(src)

    cnt = collections.Counter()
    cnt['Total PMC'] = len(df)
    cnt['Total figures'] = 0
    cnt['Empty tar.gz'] = 0
    cnt['New figures'] = 0

    data = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for _, row in tqdm.tqdm(df.iterrows(), total=len(df)):
            pmcid = row['pmcid']
            local_tgz_file = image_dir / generate_path(pmcid) / f'{pmcid}.tar.gz'
            if not local_tgz_file.exists():
                cnt['Empty tar.gz'] += 1
                continue
            futures.append(executor.submit(extract_figures, local_tgz_file=local_tgz_file, image_dir=image_dir,
                                           pmcid=pmcid))

        for future in concurrent.futures.as_completed(futures):
            d, new_figures = future.result()
            data.extend(d)
            cnt['New figures'] += new_figures
            cnt['Total figures'] += len(d)

    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    df.to_csv(dest, index=False)

    ppprint.pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figures(src=Path(args['-i']),
                dest=Path(args['-o']),
                image_dir=Path(args['-f']))

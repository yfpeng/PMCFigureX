"""
Usage:
    script.py [options] -i SOURCE -f FIGURE_DIR

Options:
    -i <file>   Figure csv file
    -f <dir>    Figure folder
"""
import tarfile
from figurex import ppprint
from figurex.commons import generate_path

import collections
from pathlib import Path

import docopt
import pandas as pd
import tqdm


def get_figures(src, image_dir):
    figure_df = pd.read_csv(src)

    cnt = collections.Counter()

    cnt['Total figures'] = len(figure_df)
    cnt['Empty tar.gz'] = 0
    cnt['New figures'] = 0
    cnt['Missing figures'] = 0

    for _, row in tqdm.tqdm(figure_df.iterrows(), total=len(figure_df)):
        pmcid = row['pmcid']
        figure_name = row['figure_name']
        local_tgz_file = image_dir / generate_path(pmcid) / f'{pmcid}.tar.gz'
        local_file = image_dir / generate_path(pmcid) / '{}_{}'.format(pmcid, figure_name)

        if not local_file.exists():
            if not local_tgz_file.exists():
                cnt['Empty tar.gz'] += 1
                continue
            t = tarfile.open(local_tgz_file, 'r')
            filename = f'{pmcid}/{figure_name}'
            try:
                r = t.extractfile(filename)
                with open(local_file, 'wb') as fp:
                    fp.write(r.read())
                cnt['New figures'] += 1
            except:
                cnt['Missing figures'] += 1
            t.close()

    ppprint.pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figures(src=Path(args['-i']),
                image_dir=Path(args['-f']))

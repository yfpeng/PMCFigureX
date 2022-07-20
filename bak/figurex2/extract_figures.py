"""
Usage:
    script.py [options] -i SOURCE -o DEST -f FIGURE_DIR

Options:
    -i <file>   CSV file with pmcid
    -o <file>   Figure CSV file
    -f <dir>    Figure folder
"""
import datetime
import tarfile
from figurex import ppprint
from figurex.commons import generate_path

import collections
from pathlib import Path

import docopt
import pandas as pd
import tqdm


def get_figures(src, dest, image_dir):
    df = pd.read_csv(src)

    cnt = collections.Counter()
    cnt['Total PMC'] = len(df)
    cnt['Total figures'] = 0
    cnt['Empty tar.gz'] = 0
    cnt['New figures'] = 0
    cnt['Missing figures'] = 0

    data = []
    insert_time = f'{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}'
    for _, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        pmcid = row['pmcid']
        local_tgz_file = image_dir / generate_path(pmcid) / f'{pmcid}.tar.gz'
        if not local_tgz_file.exists():
            cnt['Empty tar.gz'] += 1
            continue
        try:
            t = tarfile.open(local_tgz_file, 'r')
            for member in t.getmembers():
                if member.name.endswith('.jpg'):
                    local_file = image_dir / generate_path(pmcid) / '{}'.format(member.name)
                    print(local_file)
                    local_file.parent.mkdir(parents=True, exist_ok=True)
                    if not local_file.exists():
                        r = t.extractfile(member)
                        with open(local_file, 'wb') as fp:
                            fp.write(r.read())
                        cnt['New figures'] = 0
                    cnt['Total figures'] += 1
                    data.append({
                        'pmcid': pmcid,
                        'figure_name': local_file.name,
                        'insert_time': insert_time
                    })
            t.close()
        except Exception as e:
            print('%s: %s' % (pmcid, e))

        # figure_name = row['figure_name']
        # local_tgz_file = image_dir / generate_path(pmcid) / f'{pmcid}.tar.gz'
        # local_file = image_dir / generate_path(pmcid) / '{}_{}'.format(pmcid, figure_name)
        #
        # if not local_file.exists():
        #     if not local_tgz_file.exists():
        #         cnt['Empty tar.gz'] += 1
        #         continue
        #     t = tarfile.open(local_tgz_file, 'r')
        #     filename = f'{pmcid}/{figure_name}'
        #     try:
        #         r = t.extractfile(filename)
        #         with open(local_file, 'wb') as fp:
        #             fp.write(r.read())
        #         cnt['New figures'] += 1
        #     except:
        #         cnt['Missing figures'] += 1


    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    df.to_csv(dest, index=False)

    ppprint.pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figures(src=Path(args['-i']),
                dest=Path(args['-o']),
                image_dir=Path(args['-f']))

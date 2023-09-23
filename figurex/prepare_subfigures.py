"""
Usage:
    script.py [options] -i FILE -f FIGURE_DIR -o SUBFIGURE_DEST_DIR

Options:
    -i <file>           Figure CSV file
    -f <directory>      Figure folder
    -o <file>           Subfigure dest dir
"""
import collections
import os
from pathlib import Path

import docopt
import numpy as np
import pandas as pd
import tqdm

from figurex import ppprint
from figurex.commons import generate_path


def prepare_subfigure(src, dest_folder, image_dir):
    df = pd.read_csv(src)
    data = []

    cnt = collections.Counter()
    cnt['Total figures'] = 0
    cnt['New subfigures'] = 0
    cnt['Total subfigures'] = 0

    dest_image_dir = dest_folder / 'images'
    dest_label_dir = dest_folder / 'labels'

    for i, row in tqdm.tqdm(df.iterrows(), total=len(df),
                            desc='Get new subfigures'):
        pmcid = row['pmcid']
        figure_name = row['figure_name']
        figure_file = image_dir / generate_path(pmcid) / '{}/{}'.format(pmcid, figure_name)

        image_link = dest_image_dir / figure_file.name
        if not image_link.exists():
            os.symlink(figure_file, image_link)

        label_file = dest_label_dir / f'{figure_file.stem}.txt'
        if not label_file.exists():
            image_size = np.array([int(row['width']), int(row['height'])])
            np.savetxt(str(label_file), image_size)
            cnt['New subfigures'] += 1

        cnt['Total subfigures'] += len(data)

    ppprint.pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    prepare_subfigure(src=Path(args['-i']),
                      dest_folder=Path(args['-o']),
                      image_dir=Path(args['-f']))

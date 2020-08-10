"""
Usage:
    script.py [options] -i SOURCE -o DEST -f FIGURE_DIR -s SUBFIGURE_DIR -m MODEL_FILE

Options:
    -i <file>       Figure csv file
    -o <file>       Subfigure csv file
    -f <dir>        figure dir
    -s <dir>        subfigure dir
    -m <file>       model path
"""

import collections
import copy
import json
import shutil
from pathlib import Path

import docopt
import pandas as pd
import tensorflow as tf
import tqdm
from PIL import Image

from bak.figurex import FigureSeparator
from bak.figurex import is_file_empty


def split_figure(src, subfigures, dest_dir, min_width=214, min_height=214):
    filenames = []

    if len(subfigures) > 1:
        im = Image.open(src)
        for subfigure in subfigures:
            if subfigure['w'] < min_width or subfigure['h'] < min_height:
                continue
            left = subfigure['x']
            top = subfigure['y']
            right = left + subfigure['w']
            bottom = top + subfigure['h']
            dst = dest_dir / f'{src.stem}_{left}x{top}_{right}x{bottom}{src.suffix}'
            if not dst.exists():
                subim = im.crop((left, top, right, bottom))
                subim.save(dst)
            filenames.append(dst)

    return filenames


def split_figure_f(src, dest, src_image_dir, dest_image_dir, dest_json_dir, model_pathname):
    tf.compat.v1.disable_eager_execution()
    separator = FigureSeparator(str(model_pathname))
    figure_df = pd.read_csv(src)
    data = []
    cnt = collections.Counter()

    for _, row in tqdm.tqdm(figure_df.iterrows(), total=len(figure_df)):
        src = src_image_dir / row['figure filename']
        if is_file_empty(src):
            cnt['empty figure'] += 1
            continue

        json_dst = dest_json_dir / f'{src.stem}.json'
        if not json_dst.exists():
            # print(src)
            try:
                subfigures, _ = separator.extract(src)
            except:
                subfigures = []
            with open(json_dst, 'w') as fp:
                json.dump(subfigures, fp)
        else:
            with open(json_dst) as fp:
                subfigures = json.load(fp)

        pathnames = split_figure(src, subfigures, dest_image_dir, 214, 214)
        # subfigure
        for pathname in pathnames:
            x = copy.deepcopy(row)
            x['subfigure filename'] = pathname.name
            cnt['subfig'] += len(pathnames)
            cnt['figure'] += 1
            data.append(x)

        # whole figure
        pathname = dest_image_dir / src.name
        if not pathname.exists():
            shutil.copy(src, pathname)
        x = copy.deepcopy(row)
        x['subfigure filename'] = pathname.name
        cnt['figure'] += 1
        data.append(x)

    df = pd.DataFrame(data)
    df.to_csv(dest, index=False)

    for k, v in cnt.most_common():
        print(k, ':', v)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    split_figure_f(src=Path(args['-i']),
                   dest=Path(args['-o']),
                   src_image_dir=Path(args['-f']),
                   dest_image_dir=Path(args['-f']),
                   dest_json_dir=Path(args['-s']),
                   model_pathname=Path(args['-m']))


# if __name__ == '__main__':
#
#
#
#     model_pathname = ppathlib.data() / 'covid19/models/figure-separation-model-submitted-544.pb'
#
#     top = ppathlib.data() / 'covid19/covid'
#     prefix = '05092020.litcovid'
#     #
#     # top = ppathlib.data() / 'covid19/influenza'
#     # prefix = '04192020.influenza.10000'
#
#     src = top / f'{prefix}.local_figures.csv'
#     dst = top / f'{prefix}.local_subfigures.csv'
#     src_image_dir = top / 'figures'
#     dest_image_dir = top / 'figures'
#     dest_json_dir = top / 'subfigures_json'
#     split_figure_f(src, dst, src_image_dir, dest_image_dir, dest_json_dir, model_pathname)

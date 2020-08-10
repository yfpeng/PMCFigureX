"""
Usage:
    script.py [options] -d database -f figure_folder -m model_file

Options:
    -d <file>           Database file
    -f <directory>      Figure folder
    -m <file>           Model path
"""

import collections
import json
import sqlite3

import docopt
import tensorflow as tf
import tqdm

from figurex_db.db_utils import select_helper
from figurex_db.figure_separator import FigureSeparator
from figurex_db.sqlite_stmt import sql_select_empty_subfigurejsonfiles
from figurex_db.utils import generate_path
from figurex_db.utils import is_file_empty


def split_figure_f(db_file, image_dir, model_pathname, batch_size=16):
    conn = sqlite3.connect(db_file)
    df = select_helper(conn, sql_select_empty_subfigurejsonfiles, ['pmcid', 'figure_name'])
    conn.close()

    cnt = collections.Counter()
    tf.compat.v1.disable_eager_execution()
    separator = FigureSeparator(str(model_pathname))
    with tf.compat.v1.Session(graph=separator.graph) as sess:
        needs_to_split = []

        def split_and_save():
            srcs = [r[0] for r in needs_to_split]
            dsts = [r[1] for r in needs_to_split]
            results = separator.extract_batch(sess, srcs)
            assert len(results) == len(srcs)
            for dst, result in zip(dsts, results):
                subfigures = result['sub_figures']
                json.dump(subfigures, open(dst, 'w'))

        for pmcid, figure_name in tqdm.tqdm(zip(df['pmcid'], df['figure_name']), total=len(df)):
            src = image_dir / generate_path(pmcid) / '{}_{}'.format(pmcid, figure_name)
            dst = src.with_suffix('.json')
            if not dst.exists():
                needs_to_split.append((src, dst))
                if len(needs_to_split) >= batch_size:
                    split_and_save()
                    needs_to_split = []
            else:
                if is_file_empty(src):
                    cnt['empty figure'] += 1
                    continue
        if len(needs_to_split) > 0:
            split_and_save()

    for k, v in cnt.most_common():
        print(k, ':', v)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    split_figure_f(db_file=args['-d'],
                   image_dir=args['-f'],
                   model_pathname=args['-m'])

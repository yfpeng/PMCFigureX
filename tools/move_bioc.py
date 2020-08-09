"""
Usage:
    script.py -s source_dir -o dest_dir

Options:
    -s <directory>      Source folder
    -o <directory>      Dest folder
"""
import os
import shutil
from pathlib import Path

import docopt
import tqdm
from figurex_db.utils import generate_path


def move1(src_dir, dst_dir):
    with os.scandir(src_dir) as it:
        for entry in tqdm.tqdm(it):
            src = entry.path
            pmcid = Path(src).stem
            parent_dir = dst_dir / generate_path(pmcid)
            parent_dir.mkdir(parents=True, exist_ok=True)
            dst = parent_dir / f'{pmcid}.xml'
            shutil.move(src, dst)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    move1(Path(args['-s']), Path(args['-o']))

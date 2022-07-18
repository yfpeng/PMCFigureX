"""
Usage:
    script.py [options] -s <source> -d <dest>

Options:
    -s <file>      CSV source file
    -d <file>      TSV dest file
"""
from pathlib import Path

import docopt
import pandas as pd


def convert_pubmed_search_results(src, dst):
    df = pd.read_csv(src)
    df = df[['PMID', 'Title', 'Journal/Book']]
    df.columns = ['pmid', 'title', 'journal']
    df.to_csv(dst, sep='\t', index=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    convert_pubmed_search_results(Path(args['-s']), Path(args['-d']))
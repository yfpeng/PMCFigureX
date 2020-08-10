"""
Usage:
    script.py -i SOURCE -o DEST

Options:
    -i <file>       gold standard file
    -o <file>       released file
"""
import re
from pathlib import Path

import docopt
import pandas as pd


def gold_to_publish(src, dst, drop_nature=True):
    df = pd.read_csv(src)
    if drop_nature:
        df = df[df['label'] != 'nature']

    subfigures = []
    for subfigure_filename in df['subfigure filename']:
        m = re.search(r'\d+x\d+_\d+x\d+', subfigure_filename)
        if m:
            subfigures.append(m.group())
        else:
            subfigures.append(None)

    urls = []
    for pmc, figure_url in zip(df['pmcid'], df['figure url']):
        url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/bin/{figure_url}'
        urls.append(url)

    new_df  = pd.DataFrame({
        'pmcid': df['pmcid'],
        'figure url': urls,
        'subfigure': subfigures,
        'label': df['label'],
        'insert_time': df['insert_time']
    })
    new_df.to_csv(dst, index=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    gold_to_publish(src=Path(args['-i']),
                    dst=Path(args['-o']))


# if __name__ == '__main__':
#     top = ppathlib.data() / 'covid19/covid'
#     prefix = '05092020.litcovid'
#
#     src = top / f'{prefix}.local_subfigures_gold.csv'
#     dst = top / f'{prefix}.figure_list.csv'
#
#     gold_to_publish(src, dst)

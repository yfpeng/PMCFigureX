"""
Usage:
    script.py [options] -f figure_folder --ds subfigure_source_file --df figure_source_file -d text_dest_file

Options:
    -f <directory>      Figure folder
    -d <file>           Text dest file
    --df <file>         Figure source file
    --ds <file>         Subfigure source file
    --history <file>    History file
"""
import collections
import json
import re
from pathlib import Path

import bioc
from bioc.biocjson import toJSON
import docopt
import pandas as pd
import tqdm
from typing import Dict, List, Tuple

from figurex.commons import generate_path

Subfigure = collections.namedtuple('Subfigure', 'xtl ytl xbr ybr type is_subfig')


# class Subfigure:
#     def __init__(self):
#         self.xtl = 0
#         self.ytl = 0
#         self.xbr = 0
#         self.ybr = 0
#         self.type = None

class Figure:
    def __init__(self):
        self.pmcid = None
        self.url = None
        self.files = []  # type: List[Subfigure]
        self.biocid = None
        self.caption = None  # type: bioc.BioCPassage
        self.referred_text = None  # type: List[bioc.BioCPassage]

    def to_dict(self) -> Dict:
        return {
            'pmcid': self.pmcid,
            'url': self.url,
            'files': [{'xtl': s.xtl, 'ytl': s.ytl, 'xbr': s.xbr, 'ybr': s.ybr,
                       'type': s.type, 'is_subfigure': s.is_subfig}
                      for s in self.files],
            'caption': toJSON(self.caption),
            'referred_text': [toJSON(p) for p in self.referred_text]
        }


def get_figure_name(figure_path: str):
    try:
        m = re.search(r'PMC\d+_', figure_path)
    except TypeError:
        print('Cannot parse', figure_path)
        raise TypeError
    if not m:
        raise ValueError
    start = m.end()
    m = re.search(r'(_\d+x\d+_\d+x\d+)?([.][a-zA-Z]{3})$', figure_path)
    if not m:
        raise ValueError
    end = m.start()
    ext = m.group(2)
    return figure_path[start: end] + ext


def create_figures(df, history_file=None) -> List[Figure]:
    history = {}
    if history_file is not None:
        history_df = pd.read_csv(history_file)
        for figure_path, prediction in zip(history_df['figure path'], history_df['prediction']):
            history[figure_path] = prediction

    predictions = []
    for figure_path, prediction in tqdm.tqdm(zip(df['figure path'], df['prediction'])):
        if figure_path in history:
            prediction = history[figure_path]
        predictions.append(prediction)
    df['label'] = predictions
    df = df[df['label'].isin(['ct', 'cxr'])]

    figures = {}  # type: Dict[Tuple[str, str], Figure]
    for i, row in tqdm.tqdm(df.iterrows()):
        pmcid = row['pmcid']
        figure_path = row['figure path']
        figure_name = get_figure_name(figure_path)
        key = pmcid, figure_name
        # print(key)
        if key not in figures:
            figure = Figure()
            figure.pmcid = pmcid
            figure.url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/bin/{figure_name}'
            figures[key] = figure

        figure = figures[key]
        if row['type'] == 'subfigure':
            subfigure = Subfigure(row['xtl'], row['ytl'], row['xbr'], row['ybr'], row['label'], True)
            figure.files.append(subfigure)
        elif row['type'] == 'figure'and len(figure.files) == 0:
            subfigure = Subfigure(row['xtl'], row['ytl'], row['xbr'], row['ybr'], row['label'], False)
            figure.files.append(subfigure)
    return sorted(figures.values(), key=lambda f: f.pmcid)


def get_figure_reffered_text(doc: bioc.BioCDocument, figure_id):
    p = re.compile(r'(\d)+$')
    m = p.search(figure_id)
    sentences = []
    if m:
        id = int(m.group())
        s = '[F|f]ig(ure)?.?\\s{}'.format(id)
        fig_pattern = re.compile(s)
        for passage in doc.passages:
            m = fig_pattern.search(passage.text)
            if m:
                sentences.append(passage)
    return sentences


def add_text(figure: Figure, doc: bioc.BioCDocument):
    filename = figure.url[figure.url.rfind('/') + 1:]
    for p in doc.passages:
        if len(p.text) == 0:
            continue
        if 'file' in p.infons and p.infons["file"] == filename:
            id = p.infons['id']
            passages = get_figure_reffered_text(doc, id)
            figure.caption = p
            figure.referred_text = passages
            figure.id = id
            return


def get_figure_text(src1, src2, dest, history_file, bioc_dir):
    df1 = pd.read_csv(src1, dtype=str)
    df2 = pd.read_csv(src2, dtype=str)
    df = pd.concat([df1, df2], axis=0)
    figures = create_figures(df, history_file=history_file)

    docs = {}  # type: Dict[str, bioc.BioCDocument]
    for figure in figures:
        pmcid = figure.pmcid
        if pmcid not in docs:
            src = bioc_dir / generate_path(pmcid) / f'{pmcid}.xml'
            collection = bioc.load(open(src))
            docs[pmcid] = collection.documents[0]
        add_text(figure, docs[figure.pmcid])

    with open(dest, 'w', encoding='utf8') as fp:
        objs = [f.to_dict() for f in figures]
        json.dump(objs, fp, indent=2)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    if args['--history'] is not None:
        history = Path(args['--history'])
    else:
        history = None
    get_figure_text(bioc_dir=args['-f'],
                    src1=args['--df'],
                    src2=args['--ds'],
                    dest=args['-d'],
                    history_file=history)

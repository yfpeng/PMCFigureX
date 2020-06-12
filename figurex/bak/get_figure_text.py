"""
Usage:
    script.py [options] -i SOURCE -o DEST -b BIOC_DIR

Options:
    -i <file>       Gold standard file
    -o <file>       BioC Xml file
    -b <dir>        bioc dir
"""

import json
import re
from pathlib import Path
from typing import Dict, List

import bioc
import docopt
import pandas as pd
import tqdm


class OneFigure:
    def __init__(self):
        self.url = None
        self.files = []
        self.id = None
        self.caption = None  # type: bioc.BioCPassage
        self.text = None  # type: List[bioc.BioCPassage]

    def to_dict(self) -> Dict:
        return {
            'url': self.url,
            'id': self.id,
            'caption': self.caption.text,
            'text': [p.text for p in self.text],
            'files': self.files
        }

    def to_bioc_document(self) -> bioc.BioCDocument:
        doc = bioc.BioCDocument()
        doc.infons['url'] = self.url
        doc.infons['figure id'] = self.id
        doc.infons['files'] = json.dumps(self.files)

        self.caption.infons['type'] = 'caption'
        doc.add_passage(self.caption)

        for p in self.text:
            p.infons['type'] = 'text'
            doc.add_passage(p)

        return doc


class OneArticle:
    def __init__(self):
        self.pmcid = None
        self.figures = {}  # type: Dict[str, OneFigure]
        self.pmid = None
        self.doi = None
        self.title = None
        self.journal = None
        self.pubdate = None

    @classmethod
    def clean_up(cls, articles: List['OneArticle']) -> List['OneArticle']:
        new_articles = []
        for article in articles:
            new_figures = {}
            for url, fig in article.figures.items():
                if fig.files:
                    new_figures[url] = fig
            if new_figures:
                article.figures = new_figures
                new_articles.append(article)
        return new_articles

    def to_bioc_document(self) -> List[bioc.BioCDocument]:
        rst = []
        for f in self.figures.values():
            doc = f.to_bioc_document()
            doc.id = f'{self.pmcid}_{f.id}'
            # doc.infons['pmcid'] = self.pmcid
            # doc.infons['pmid'] = self.pmid
            # doc.infons['title'] = self.title
            # doc.infons['journal'] = self.journal
            # doc.infons['pubdate'] = self.pubdate
            # doc.infons['doi'] = self.doi
            rst.append(doc)
        return rst

    def to_dict(self) -> Dict:
        return {
            'pmcid': self.pmcid,
            'pmid': self.pmid,
            'title': self.title,
            'journal': self.journal,
            'pubdate': self.pubdate,
            'doi': self.doi,
            'figures': list(f.to_dict() for f in self.figures.values())
        }


def df_to_obj(df) -> List[OneArticle]:
    df = df[df['label'].isin(['ct', 'cxr'])]

    objs = {}  # type: Dict[str, OneArticle]
    for _, row in tqdm.tqdm(df.iterrows()):
        pmcid = row['pmcid']
        article = OneArticle()
        article.pmcid = pmcid
        objs[pmcid] = article

    # figure url, caption, filename
    for _, row in tqdm.tqdm(df.iterrows()):
        article = objs[row['pmcid']]
        url = row['figure url']
        if url not in article.figures:
            fig = OneFigure()
            fig.url = url
            article.figures[url] = fig

    # subfigure
    for _, row in tqdm.tqdm(df.iterrows()):
        fig = objs[row['pmcid']].figures[row['figure url']]
        fig.files.append({'filename': row['subfigure filename'], 'type': row['label']})

    l = OneArticle.clean_up(sorted(objs.values(), key=lambda a: a.pmcid))
    return l


def get_doi(aid):
    for x in aid:
        if x.endswith('[doi]'):
            return x[: -len(' [doi]')]
    return None


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


def get_figure_caption(figure: OneFigure, doc):
    filename = figure.url[figure.url.rfind('/') + 1:]
    for p in doc.passages:
        if len(p.text) == 0:
            continue
        if 'file' in p.infons and p.infons["file"] == filename:
            id = p.infons['id']
            passages = get_figure_reffered_text(doc, id)
            figure.caption = p
            figure.text = passages
            figure.id = id
            return


def add_text(objs: List[OneArticle], bioc_dir):
    for obj in objs:
        pmcid = obj.pmcid
        with open(bioc_dir / f'{pmcid}.xml', encoding='utf8') as fp:
            collection = bioc.load(fp)
            for doc in collection.documents:
                # split sentences
                # doc = split_sentences(doc)
                for figure in obj.figures.values():
                    get_figure_caption(figure, doc)
    return objs


def get_figure_text(src, dest, bioc_dir):
    df = pd.read_csv(src, dtype=str)
    objs = df_to_obj(df)

    # add text
    objs = add_text(objs, bioc_dir)

    collection = bioc.BioCCollection()
    for obj in objs:
        collection.documents.extend(obj.to_bioc_document())
    with open(dest, 'w', encoding='utf8') as fp:
        bioc.dump(collection, fp)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figure_text(src=Path(args['-i']),
                    dest=Path(args['-o']),
                    bioc_dir=Path(args['-b']))

# if __name__ == '__main__':
#     top = ppathlib.data() / 'covid19/covid'
#     prefix = '05092020.litcovid'
#     gold = top / '05092020.litcovid.local_subfigures_gold.csv'
#
#     # top = ppathlib.data() / 'covid19/influenza'
#     # prefix = '04192020.influenza.10000'
#     # gold = top / '04192020.influenza.10000.local_subfigures_gold.csv'
#
#     src = top / f'{prefix}.local_subfigures_pred.csv'
#     dst = top / f'{prefix}.local_subfigures_cxr_ct.xml'
#     get_figure_text(src, dst, gold, top / 'bioc', top / 'medline')

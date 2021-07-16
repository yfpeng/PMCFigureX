"""
Usage:
    script.py [options] -f figure_folder -s text_json_file -d html_file --disease disease --neg neg_file

Options:
    -f <directory>      Figure folder
    -s <file>           Text json file
    -d <file>           HTML file
    --neg <file>        neg file
    --disease <str>     Disease name
    --standalone
"""

import collections
import json
import shutil
from pathlib import Path
from typing import Type

import bioc
import docopt
import tqdm
from PIL import Image
from bioc import BioCDocument
from dominate.util import raw
from dominate.tags import img, h3, p, ul, li, html, body, hr, h1, span, table, tbody, tr, td, head, title

from figurex_db.utils import generate_path


def has_keyword(bdoc: BioCDocument, disease, include_neg=True):
    for p in bdoc.passages:
        if include_neg and len(p.annotations) > 0:
            return True
        for ann in p.annotations:
                if ann.infons['preferred_name'] == disease:
                    if include_neg:
                        return True
                    elif 'negation' not in ann.infons or not ann.infons['negation']:
                        return True
        if len(p.annotations) > 0:
            return True
    return False


def start(passage, i):
    for ann in passage.annotations:
        if ann.total_span.offset - passage.offset == i:
            return True, 'negation' in ann.infons
    return False, False


def end(passage, i):
    for ann in passage.annotations:
        if ann.total_span.offset + len(ann.text) - passage.offset == i:
            return True
    return False


def get_text(bpassage):
    text = bpassage.text
    color_text = ''
    for i, char in enumerate(text):
        is_start, is_neg = start(bpassage, i)
        if is_start:
            if is_neg:
                color_text += '<span style="color:red;">'
            else:
                color_text += '<span style="color:blue;">'
        is_end = end(bpassage, i)
        if is_end:
            color_text += '</span>'
        color_text += char
    return color_text


def to_html(bioc_dir, src, dest, disease, neg_file, is_standalone=False):
    if is_standalone:
        dest_img_dir = dest.parent / 'images'
        if not dest_img_dir.exists():
            dest_img_dir.mkdir()

    with open(src) as fp:
        objs = json.load(fp)

    with open(neg_file) as fp:
        neg_collection = bioc.load(fp)
    url_map = {}
    for doc in neg_collection.documents:
        url_map[doc.infons['figure_url']] = doc

    _html = html()
    _head, _body = _html.add(head(title(disease)), body())

    cnt = collections.Counter()
    for i, doc in tqdm.tqdm(enumerate(objs)):
        bdoc = url_map[doc['url']]

        if not has_keyword(bdoc, disease):
            cnt['No'] += 1
            continue

        _body.add(hr())

        pmcid = doc['pmcid']

        with _body:
            # meta
            h1('PMC: {}'.format(doc['pmcid']))

            # get caption
            h3('Caption')
            p(raw(get_text(bdoc.passages[0])))

            # get referred text
            if doc['referred_text']:
                h3('Referred text')
                with ul():
                    for bpassage in bdoc.passages[1:]:
                        li(raw(get_text(bpassage)))

        figure_name = doc['url']
        figure_name = figure_name[figure_name.rfind('/') + 1:]
        # get figure
        figure_file = bioc_dir / generate_path(pmcid) / '{}_{}'.format(pmcid, figure_name)
        # get subfigure
        _table = table()
        _body.add(_table)
        row1 = tr()
        row2 = tr()
        for subfigure in doc['files']:
            if subfigure['type'] in ['ct', 'cxr']:
                if subfigure['is_subfigure']:
                    xtl = subfigure['xtl']
                    ytl = subfigure['ytl']
                    xbr = subfigure['xbr']
                    ybr = subfigure['ybr']
                    local_file = figure_file.parent / f'{figure_file.stem}_{xtl}x{ytl}_{xbr}x{ybr}{figure_file.suffix}'
                else:
                    local_file = figure_file

                im = Image.open(local_file)

                if is_standalone:
                    local_file = dest_img_dir / local_file.name
                    if not local_file.exists():
                        shutil.copy(local_file, local_file)
                    local_file = local_file.relative_to(dest.parent)

                # local_file = local_file.relative_to(dest)
                if im.width > im.height:
                    _img = img(src=str(local_file), width=300)
                else:
                    _img = img(src=str(local_file), height=300)
                row1.add(td(_img))
                row2.add(td('ID: {}, Type: {}'.format(doc['caption']['infons']['id'], subfigure['type'])))
        _table.add(row1)
        _table.add(row2)
        cnt[disease] += 1

        # if i >= 10:
        #     break

    with open(dest, 'w') as fp:
        fp.write(str(_html))

    print(cnt)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    to_html(bioc_dir=Path(args['-f']), src=Path(args['-s']), dest=Path(args['-d']), disease=args['--disease'],
            is_standalone=args['--standalone'], neg_file=args['--neg'])
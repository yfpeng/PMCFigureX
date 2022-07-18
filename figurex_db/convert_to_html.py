"""
Usage:
    script.py [options] -f figure_folder -s text_json_file -d html_file --disease disease

Options:
    -f <directory>      Figure folder
    -s <file>           Text json file
    -d <file>           HTML file
    --disease <str>     Disease name
    --standalone
"""

import collections
import json
import shutil
from pathlib import Path

import docopt
import tqdm
from PIL import Image
from dominate.tags import img, h3, p, ul, li, html, body, hr, h1, span, table, tbody, tr, td, head, title

from figurex_db.utils import generate_path


def filter_text(text, key):
    return key.lower() in text.lower()


def has_keyword(doc, key):
    if filter_text(doc['caption']['text'], key):
        return True
    for r in doc['referred_text']:
        if filter_text(r['text'], key):
            return True
    return False


def to_html(bioc_dir, src, dest, disease, is_standalone=False):
    if is_standalone:
        dest_img_dir = dest.parent / 'images'
        if not dest_img_dir.exists():
            dest_img_dir.mkdir()

    with open(src) as fp:
        objs = json.load(fp)

    _html = html()
    _head, _body = _html.add(head(title(disease)), body())

    cnt = collections.Counter()
    for i, doc in tqdm.tqdm(enumerate(objs)):
        if not has_keyword(doc, disease):
            continue

        _body.add(hr())

        pmcid = doc['pmcid']

        with _body:
            # meta
            h1('PMC: {}'.format(doc['pmcid']))

            # get caption
            h3('Caption')
            p(doc['caption']['text'])

            # get referred text
            if doc['referred_text']:
                h3('Referred text')
                with ul():
                    for r in doc['referred_text']:
                        li(r['text'])

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
            is_standalone=args['--standalone'])
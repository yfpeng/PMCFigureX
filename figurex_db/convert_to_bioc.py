"""
Usage:
    script.py [options] -s text_json_file -d bioc_file

Options:
    -s <file>           Text json file
    -d <file>           BioC file
"""

import json
from pathlib import Path

import bioc
import docopt
import tqdm


def to_bioc(src, dest):
    with open(src) as fp:
        objs = json.load(fp)

    c = bioc.BioCCollection()
    for i, doc in tqdm.tqdm(enumerate(objs)):
        bdoc = bioc.BioCDocument()
        bdoc.id = doc['pmcid']

        # caption
        passage = bioc.BioCPassage()
        passage.infons = doc['caption']['infons']
        passage.offset = doc['caption']['offset']
        passage.text = doc['caption']['text']
        bdoc.add_passage(passage)

        # get referred text
        if doc['referred_text']:
            offset = len(passage.text) + 1
            for r in doc['referred_text']:
                passage = bioc.BioCPassage()
                passage.infons = r['infons']
                passage.offset = r['offset']
                passage.text = r['text']
                bdoc.add_passage(passage)
                offset += len(passage.text) + 1

        bdoc.infons['figure_url'] = doc['url']
        c.add_document(bdoc)

    with open(dest, 'w') as fp:
        bioc.dump(c, fp)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    to_bioc(src=Path(args['-s']), dest=Path(args['-d']))

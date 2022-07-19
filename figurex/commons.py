import os
import urllib.request
from pathlib import Path
from typing import List

import bioc


def get_bioc(pmid, dest):
    url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmid}/unicode'
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, 'w', encoding='utf8') as fp:
        fp.write(text)


def is_file_empty(pathanme):
    return os.path.exists(pathanme) and os.stat(pathanme).st_size == 0


def create_empty_file(pathname):
    with open(pathname, 'w') as _:
        pass


def generate_path(pmc: str) -> Path:
    return Path(pmc[:-4] + '/' + pmc[-4:-2])


FIG_PASSAGE = {"fig_caption",
               "fig_title_caption",
               "fig",
               "fig_footnote",
               "fig_footnote_caption",
               "fig_footnote_title_caption"}


def get_figure_link(biocfile) -> List[str]:
    try:
        with open(biocfile, 'r', encoding='utf8') as fp:
            c = bioc.load(fp)
    except Exception as e:
        raise e
    figures = []
    for doc in c.documents:
        for p in doc.passages:
            if len(p.text) == 0:
                continue
            p.text = p.text.replace('\n', ' ')
            if 'file' in p.infons and 'type' in p.infons and p.infons['type'] in FIG_PASSAGE:
                figures.append(p.infons["file"])
    return figures

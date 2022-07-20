import os
import urllib.request
from pathlib import Path


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
    pathname.parent.mkdir(parents=True, exist_ok=True)
    with open(pathname, 'w') as _:
        pass


def generate_path(pmc: str) -> Path:
    return Path(pmc[:-4] + '/' + pmc[-4:-2])



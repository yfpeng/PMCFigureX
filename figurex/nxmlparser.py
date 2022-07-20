from pathlib import Path

from lxml import etree


def get_figs(input):
    tree = etree.parse(str(input))
    root = tree.getroot()
    for fig_elem in root.findall('.//fig'):
        print(fig_elem.attrib['id'])


if __name__ == '__main__':
    top_dir = Path.home() / 'Data/PMCFigureX/edema'
    get_figs(top_dir / 'ymj-46-1.nxml')

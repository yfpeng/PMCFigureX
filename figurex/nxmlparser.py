from pathlib import Path

from lxml import etree


def get_figs(input):
    tree = etree.parse(str(input))
    root = tree.getroot()
    for fig_elem in root.findall('.//fig'):
        print(fig_elem.attrib['id'])
        print(fig_elem.find('label'))
        print(fig_elem.find('caption'))
        print(fig_elem.find('graphic'))


if __name__ == '__main__':
    top_dir = Path.home() / 'Data/derm'
    get_figs(top_dir / '1757-1626-1-263.nxml')

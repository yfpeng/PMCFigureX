import os
from pathlib import Path
import re


def parse_subfigure_path(pathname: str):
    path = Path(pathname)
    name = path.name
    m = re.search(r'(\d+)x(\d+)_(\d+)x(\d+)', name)
    assert m is not None
    xtl = int(m.group(1))
    ytl = int(m.group(2))
    xbr = int(m.group(3))
    ybr = int(m.group(4))
    local_figure_name = name[:m.start()-1] + name[m.end():]
    index = local_figure_name.find('_')
    pmc = local_figure_name[:index]
    figure_name = local_figure_name[index+1:]
    return {'pmcid': pmc,
            'pmc_figure_name': figure_name,
            'local_figure_name': local_figure_name,
            'xtl': xtl,
            'ytl': ytl,
            'xbr': xbr,
            'ybr': ybr}


def parse_figure_path(pathname: str):
    path = Path(pathname)
    local_figure_name = path.name
    index = local_figure_name.find('_')
    pmc = local_figure_name[:index]
    figure_name = local_figure_name[index+1:]
    return {'pmcid': pmc,
            'pmc_figure_name': figure_name,
            'local_figure_name': local_figure_name}



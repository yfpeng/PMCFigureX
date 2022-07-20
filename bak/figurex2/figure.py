import re
from typing import List, Dict, Set

import bioc

class Figure:
    def __init__(self):
        self.pmcid = None
        self.id = None
        self.referred_id = None
        self.fig_passages = []  # type: List[bioc.BioCPassage]
        self.referred_passages = []  # type: List[bioc.BioCPassage]

    # def to_dict(self) -> Dict:
    #     return {
    #         'pmcid': self.pmcid,
    #         'url': self.url,
    #         'files': [{'xtl': s.xtl, 'ytl': s.ytl, 'xbr': s.xbr, 'ybr': s.ybr,
    #                    'type': s.type, 'is_subfigure': s.is_subfig}
    #                   for s in self.files],
    #         'caption': toJSON(self.caption),
    #         'referred_text': [toJSON(p) for p in self.referred_text]
    #     }


FIG_PASSAGE = {"fig_caption",
               "fig_title_caption",
               "fig",
               "fig_footnote",
               "fig_footnote_caption",
               "fig_footnote_title_caption"}


def get_figure_link(doc: bioc.BioCDocument) -> List[Figure]:
    figures = []
    for p in doc.passages:
        if 'file' in p.infons \
                and 'type' in p.infons and p.infons['type'] in FIG_PASSAGE:
            figures.append(p.infons["file"])
    return figures


def get_fig(doc: bioc.BioCDocument) -> Set[Figure]:
    figures = {}  # type: Dict[str, Figure]
    for p in doc.passages:
        if 'file' in p.infons and 'id' in p.infons \
                and ('type' in p.infons and p.infons['type'] in FIG_PASSAGE):
            id = p.infons['id']
            if id not in figures:
                fig = Figure()
                fig.id = id
                m = re.search(r'(\d)+$', id)
                if m:
                    fig.referred_id = int(m.group())
                figures[id] = fig
            figures[id].fig_passages.append(p)
    return figures.values()


def has_referred_id(figure: Figure, passage: bioc.BioCPassage):
    s = '[F|f]ig(ure)?.?\\s{}'.format(figure.referred_id)
    p = re.compile(s)
    m = p.search(passage.text)
    return m is not None


def get_fig_others(figure: Figure, doc: bioc.BioCDocument):
    for p in doc.passages:
        # referred text
        if has_referred_id(figure, p):
            figure.referred_passages.append(p)
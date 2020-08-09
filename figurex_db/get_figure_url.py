"""
Usage:
    script.py [options] -d database -b bioc_folder

Options:
    -d <file>           Database file
    -b <directory>      BioC folder
"""

import datetime
import sqlite3
from pathlib import Path
from typing import List

import bioc
import docopt
import tqdm

from figurex_db.db_utils import DBHelper, select_helper
from figurex_db.utils import generate_path

FIG_PASSAGE = {"fig_caption",
               "fig_title_caption",
               "fig",
               "fig_footnote",
               "fig_footnote_caption",
               "fig_footnote_title_caption"}


def get_figure_link(biocfile) -> List[str]:
    try:
        c = bioc.load(open(biocfile, 'r', encoding='utf8'))
    except:
        return []
    figures = []
    for doc in c.documents:
        for p in doc.passages:
            if len(p.text) == 0:
                continue
            p.text = p.text.replace('\n', ' ')
            if 'file' in p.infons and 'type' in p.infons and p.infons['type'] in FIG_PASSAGE:
                figures.append(p.infons["file"])
    return figures


sql_select_new_bioc = """
SELECT      DISTINCT t1.pmcid
FROM        Articles AS t1
LEFT JOIN   Figures AS t2
ON          t1.pmcid = t2.pmcid
WHERE       t2.pmcid IS NULL 
AND         t1.has_bioc = 1
AND         (t1.has_figure == 1 OR t1.has_figure IS NULL);
"""

sql_insert_figure = """
INSERT INTO Figures(pmcid, figure_name, insert_time) 
VALUES      (?,?,?);
"""

sql_update_has_figure1 = """
UPDATE Articles
SET    has_figure = 1
WHERE  pmcid IN (
    SELECT    a.pmcid
    FROM      Articles AS a
    LEFT JOIN Figures AS f
    ON        a.pmcid = f.pmcid
    WHERE     f.pmcid IS NOT NULL
    AND       a.has_bioc = 1);
"""

sql_update_has_figure0 = """
UPDATE Articles
SET    has_figure = 0
WHERE  pmcid IN (
    SELECT    a.pmcid
    FROM      Articles AS a
    LEFT JOIN Figures AS f
    ON        a.pmcid = f.pmcid
    WHERE     f.pmcid IS NULL
    AND       a.has_bioc = 1);
"""


def get_figure_url(db_file, bioc_dir):
    conn = sqlite3.connect(db_file)

    df = select_helper(conn, sql_select_new_bioc, ['pmcid'])
    #
    insert_time = f'{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}'
    insert_helper = DBHelper(conn, sql_insert_figure)
    insert_helper.start()
    for pmcid in tqdm.tqdm(df['pmcid'], total=len(df)):
        biocfile = bioc_dir / generate_path(pmcid) / f'{pmcid}.xml'
        figure_names = get_figure_link(biocfile)
        insert_helper.extend(set([(pmcid, figure_name, insert_time) for figure_name in figure_names]))
    insert_helper.finish()

    # update has_figure
    c = conn.cursor()
    c.execute(sql_update_has_figure0)
    c.execute(sql_update_has_figure1)
    conn.commit()

    conn.close()


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figure_url(args['-d'], Path(args['-b']))

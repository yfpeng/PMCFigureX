"""
Usage:
    script.py [options] -d database

Options:
    -d <file>       Database file
"""

import sqlite3

import docopt

sql_create_articles_table = """
CREATE TABLE IF NOT EXISTS Articles (
    pmcid       TEXT PRIMARY KEY,
    pmid        TEXT,
    doi         TEXT,
    has_bioc    INTEGER,
    has_medline INTEGER,
    has_figure  INTEGER,
    insert_time TEXT
);
"""

sql_create_figures_table = """
CREATE TABLE IF NOT EXISTS Figures (
    pmcid         TEXT,
    figure_name   TEXT,
    width         INTEGER,
    height        INTEGER,
    has_subfigure INTEGER,
    insert_time   TEXT,
    PRIMARY KEY (pmcid, figure_name)
);
"""

sql_create_subfigures_table = """
CREATE TABLE IF NOT EXISTS Subfigures (
    pmcid       TEXT,
    figure_name TEXT,
    xtl         INTEGER,
    ytl         INTEGER,
    xbr         INTEGER,
    ybr         INTEGER
    label       TEXT,
    labeler     TEXT,
    insert_time TEXT
);
"""


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(sql_create_articles_table)
    c.execute(sql_create_figures_table)
    c.execute(sql_create_subfigures_table)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    create_connection(args['-d'])

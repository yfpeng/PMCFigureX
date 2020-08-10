"""
Usage:
    script.py [options] -d database

Options:
    -d <file>       Database file
"""

import sqlite3

import docopt

from figurex_db.sqlite_stmt import sql_create_articles_table, sql_create_figures_table, sql_create_subfigures_table


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

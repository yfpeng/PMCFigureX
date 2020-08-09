import collections
import logging

import pandas as pd


def select_helper(conn, sql_stmt, columns):
    c = conn.cursor()
    c.execute(sql_stmt)
    rows = [row for row in c.fetchall()]
    return pd.DataFrame(rows, columns=columns)


class DBHelper:
    def __init__(self, conn, sql_stmt, bulk_size=500):
        self.conn = conn
        self.sql_stmt = sql_stmt
        self.bulk_size = bulk_size
        self.records = []
        self.cnt = collections.Counter()

    def start(self):
        del self.records[:]

    def append(self, record):
        self.records.append(record)
        if len(self.records) >= self.bulk_size:
            self.commit()

    def extend(self, records):
        self.records.extend(records)
        if len(self.records) >= self.bulk_size:
            self.commit()

    def commit(self):
        if self.records:
            c = self.conn.cursor()
            c.executemany(self.sql_stmt, self.records)
            del self.records[:]
            self.conn.commit()
            self.cnt['Commit'] += c.rowcount
            logging.debug('Commit %s rows', c.rowcount)

    def finish(self):
        if self.records:
            self.commit()

    def summarize(self):
        print('Summarize:')
        if self.cnt:
            for k, v in self.cnt.most_common():
                print(k, ':', v)
        else:
            print('No change')

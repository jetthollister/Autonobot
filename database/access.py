import sqlite3 as sqlite
from sqlite3 import Error


class Database:

    def sqlConnect(path):

        conn = None
        try:
            conn = sqlite.connect(path)
            return conn

        except Error as e:
            print(e)

        return conn

    def createTable(conn):

        try:
            c = conn.cursor()

            prompt = """ CREATE TABLE IF NOT EXISTS reportedTrends(
                                       trend TEXT,
                                       UNIQUE (trend) ON CONFLICT IGNORE
                                       ); """
            c.execute(prompt)

        except Error as e:
            print(e)

        return

    def loadDb(conn):

        with conn:

            conn.row_factory = sqlite.Row
            c = conn.cursor()
            c.execute('SELECT * FROM reportedTrends')
            rows = c.fetchall()

        return [row['trend'] for row in rows]

    def writeDb(conn, df):

        with conn:

            c = conn.cursor()
            for trend in df:
                c.execute("INSERT INTO reportedTrends VALUES (?)",
                          (trend,))
        return

    def deleteAll(conn):

        with conn:
            c = conn.cursor()
            c.execute('DELETE FROM reportedTrends')

        return

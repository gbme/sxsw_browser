import sqlite3
conn = sqlite3.connect('/vagrant/sxsw.db')
import requests

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn.row_factory = dict_factory
c = conn.cursor()


def main():
    c.execute('''SELECT eventid,userid FROM sxsw_user_events''')
    r = c.fetchall()
    for a in r:
        print a
        rq = requests.post("https://test.gbme.nl/sxsw_store/users/"+a["userid"]+"/events/"+a["eventid"])        
        print rq.status_code


main()
from bottle import route,post,delete,get, run, template,request,redirect,response,static_file
import requests
import json

import log
logger = log.setup('root','sxsw.log')

import sqlite3
conn = sqlite3.connect('/vagrant/sxsw.db')

port = 8081

logger.debug(conn)
def create_tables():
    try:
        c.execute("CREATE TABLE sxsw_user_events (userid text, eventid text,CONSTRAINT name_unique UNIQUE (userid,eventid))")
        conn.commit()
    except e:
        logger.exception(e)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn.row_factory = dict_factory
c = conn.cursor()

def test_db():
    try:
        c.execute("SELECT * from sxsw_user_events LIMIT 1")
    except:
        logger.debug( "error, recreateing table")
        create_tables()

test_db()

@post('/users/<userid>/events/<eventid>')
def index(userid,eventid):
    logger.debug( eventid)
    c.execute("REPLACE INTO sxsw_user_events VALUES (?,?)",(userid,eventid))
    conn.commit()
    if update_elastic(eventid):
        return "ACK" 
    return "NACK"

def update_elastic(eventid):
    try:
        headers = {'Content-type': 'application/json', "authtoken":"gbme"}
        attendees = get_all_attendees(eventid)
        logger.debug( attendees)
        elastic_update =  {
    
           "doc" : {
              "attendees" : attendees
            }
        }
        r = requests.post("http://localhost:9200/sxswevents/event/"+eventid+".json/_update",data=json.dumps(elastic_update), headers=headers)
        logger.debug( r.text)
        res = json.loads(r.text)
        if res["_shards"]["successful"]==1:
            return True
        else:
            return False 
    except e:
        logger.exception("error in update_elastic")
        return False



@delete('/users/<userid>/events/<eventid>')
def index(userid,eventid):
    logger.debug( eventid)
    c.execute("DELETE FROM sxsw_user_events WHERE userid=? AND eventid=?",(userid,eventid))
    conn.commit()
    if update_elastic(eventid):
        return "ACK" 
    return "NACK"



def get_all_attendees(eventid):
    c.execute('''SELECT userid FROM sxsw_user_events WHERE eventid=?''',(eventid,))
    r = c.fetchall()
    res = []
    for a in r:
        res.append(a["userid"])
    return res

@get('/events/<eventid>/users/')
def index(eventid):
    try:
        logger.debug("get users for event:"+eventid)
        c.execute('''SELECT userid FROM sxsw_user_events WHERE eventid=?''',(eventid,))
        r = c.fetchall()
        return json.dumps(r)
    except e:
        logger.exception("err")


@get('/users/<userid>/events/')
def index(userid):
    c.execute('''SELECT eventid FROM sxsw_user_events WHERE userid=?''',(userid,))
    r = c.fetchall()
    return json.dumps(r)
    
logger.debug("starting server at:"+str(port))
    
run(host='localhost', port=port)
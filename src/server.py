from bottle import route, post, delete, get, run, template, request, redirect, response, static_file
import requests
import json
from datetime import datetime, timedelta
import log
import uuid
import urllib
import config as CONFIG
logger = log.setup('root', 'sxsw.log')
from email.utils import parseaddr
from passlib.apps import custom_app_context as pwd_context
import os
import sqlite3
import secrets

#token = secrets.global_config.slackkey      # found at https://api.slack.com/web#authentication

#sc = SlackClient(token)
#print sc.api_call("api.test")


authdir = "/vagrant/auth/"
conn = sqlite3.connect('/vagrant/sxsw2.db')
logger.debug(CONFIG)
logger.debug(CONFIG.global_config.domain)
domain = CONFIG.global_config.domain
app_root = CONFIG.global_config.app_root
static_root = CONFIG.global_config.static_root
protocol = CONFIG.global_config.protocol
base_url = protocol + domain + "/" + app_root
homepage = protocol + domain + "/" + static_root + "/"
cookiedomain = domain
port = 8081
logger.debug(domain)


class DecimalEncoder(json.JSONEncoder):
    def totimestamp(self, dt, epoch=datetime(1970, 1, 1)):
        td = dt - epoch
        # return td.total_seconds()
        return int(((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 1e3) + (
            0 * 3600000))

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime):
            return self.totimestamp(o)
        return super(DecimalEncoder, self).default(o)


class JSONPlugin(object):
    name = 'jsonapi'
    api = 1

    def apply(self, callback, context):
        def wrapper(*a, **ka):
            try:
                r = callback(*a, **ka)
                # Attempt to serialize, raises exception on failure
                json_response = json.dumps(r, cls=DecimalEncoder)

                # Set content type only if serialization succesful
                response.content_type = 'application/json'

                # Wrap in callback function for JSONP
                callback_function = request.GET.get('callback')
                if callback_function:
                    json_response = ''.join([callback_function, '(', json_response, ')'])
                # logger.debug(json_response)
                return json_response
            except:
                logger.exception("error")
                return False

        return wrapper


jsonp_plugin = JSONPlugin()

logger.debug(conn)


def touch(fname, times=None):
    fhandle = open(fname, 'a')
    try:
        os.utime(fname, times)
    finally:
        fhandle.close()


def create_table_user_events():
    try:
        c.execute(
            "CREATE TABLE sxsw_user_events (userid TEXT, eventid TEXT,CONSTRAINT name_unique UNIQUE (userid,eventid))")
        conn.commit()
    except:
        logger.exception("")


def create_table_users():
    try:
        c.execute("CREATE TABLE sxsw_users (userid INTEGER PRIMARY KEY AUTOINCREMENT, "
                  "email TEXT, "
                  "uuid TEXT,"
                  "handle TEXT, "
                  "user_token TEXT, "
                  "hash TEXT, "
                  "admin INT, "
                  "invite_token TEXT, "
                  "invite_created INT, "
                  "active INT, reset_token TEXT, "
                  "reset_date INT, "
                  "last_login INT, "
                  "csrf_token TEXT)")
        conn.commit()

    except:
        logger.exception("")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


conn.row_factory = dict_factory
c = conn.cursor()


def test_db():
    try:
        c.execute("SELECT * FROM sxsw_user_events LIMIT 1")
    except:
        logger.debug("error, recreateing table")
        create_table_user_events()
    try:
        c.execute("SELECT * FROM sxsw_users LIMIT 1")
    except:
        logger.debug("error, recreateing table")
        create_table_users()


test_db()

def check_user():
    #check is user is logged in
    auth_cookie = request.get_cookie('AUTH_COOKIE')
    logger.debug("auth cookie:"+auth_cookie)
    if auth_cookie and os.path.isfile(authdir+auth_cookie):
        logger.debug("file exists")
        c.execute("SELECT * FROM sxsw_users WHERE uuid=?", (auth_cookie,))
        user = c.fetchone()
        return user
    else:
        logger.debug("no such login cookie")
        return


@post('/users/<userid>/events/<eventid>')
def index(userid, eventid):
    user = check_user()
    if user:
        logger.debug(eventid)
        c.execute("REPLACE INTO sxsw_user_events VALUES (?,?)", (userid, eventid))
        conn.commit()
        if update_elastic(eventid):
            return "ACK"
    return "Not logged in"


def update_elastic(eventid):
    try:
        headers = {'Content-type': 'application/json', "authtoken": "gbme"}
        attendees = get_all_attendees(eventid)
        logger.debug(attendees)
        elastic_update = {

            "doc": {
                "attendees": attendees
            }
        }
        r = requests.post("http://localhost:9200/sxswevents/event/" + eventid + ".json/_update",
                          data=json.dumps(elastic_update), headers=headers)
        logger.debug(r.text)
        res = json.loads(r.text)
        if res["_shards"]["successful"] == 1:
            return True
        else:
            return False
    except e:
        logger.exception("error in update_elastic")
        return False


@delete('/users/<userid>/events/<eventid>')
def index(userid, eventid):
    logger.debug(eventid)
    user = check_user()
    if user:
        c.execute("DELETE FROM sxsw_user_events WHERE userid=? AND eventid=?", (userid, eventid))
        conn.commit()
        if update_elastic(eventid):
            return "ACK"
    return "Not logged in"


def get_all_attendees(eventid):
    c.execute('''SELECT userid FROM sxsw_user_events WHERE eventid=?''', (eventid,))
    r = c.fetchall()
    res = []
    for a in r:
        res.append(a["userid"])
    return res


@get('/events/<eventid>/users/')
def index(eventid):
    try:
        logger.debug("get users for event:" + eventid)
        c.execute('''SELECT userid FROM sxsw_user_events WHERE eventid=?''', (eventid,))
        r = c.fetchall()
        return json.dumps(r)
    except e:
        logger.exception("err")


@get('/users/<userid>/events/')
def index(userid):
    c.execute('''SELECT eventid FROM sxsw_user_events WHERE userid=?''', (userid,))
    r = c.fetchall()
    return json.dumps(r)


def get_all_users():
    c.execute("SELECT handle FROM sxsw_users ORDER BY handle")
    users = c.fetchall()
    return users

@get("/api/auth/check", apply=[jsonp_plugin])
def auth_check():
    try:
        logger.debug("check")
        expires = (datetime.today() + timedelta(minutes=3600))
        auth_cookie = request.get_cookie('AUTH_COOKIE')
        logger.debug(auth_cookie)
        if not (auth_cookie) or not (os.path.isfile("/vagrant/auth/" + auth_cookie)):
            logger.debug("no cookie, login again")
            result = {"loggedin": False, "loginpage": "/login"}
            return result

        c.execute("SELECT * FROM sxsw_users WHERE uuid=?", (auth_cookie,))
        res = c.fetchone()
        logger.debug(res)
        if res:
            logger.debug("check ok")
            response.set_cookie("AUTH_COOKIE", auth_cookie, expires=expires, domain=cookiedomain, path="/")
            result = {"user_token": res.get("user_token"),
                      "csrf_token": res.get("csrf_token"), "loggedin": True, "email": res["email"],"userid":res["userid"],"handle":res["handle"]}
        else:
            response.delete_cookie("AUTH_COOKIE")
            result = {"loggedin": False}
            logger.debug(result)
            logger.debug(result)
        return result
    except:
        logger.exception("err")


def test_email(text):
    r = parseaddr(text)[1]
    if '@' in r:
        return r


def unique_id():
    return uuid.uuid4().hex


def input_cleaner(text):
    return text.replace("<", "")


def send_simple_message(email, token, template, handler,subject):
    template = open("/vagrant/src/templates/" + template).read()
    if template:
        text = template.replace("{{url}}", homepage + "/" + handler + "?email=" + email + "&token=" + token)
        logger.debug(text)
        return requests.post(
            "https://api.mailgun.net/v2/gbme.nl/messages",
            auth=("api", "key-9fa82127b18561758f4809985b438922"),
            data={"from": "gbme <gerbrand@gbme.nl>",
                  "to": [email],
                  "subject": subject,
                  "html": text})
    else:
        throw("no template found")


def logout(message = False):
    auth_cookie = request.get_cookie('AUTH_COOKIE')
    logger.debug("logout")
    if auth_cookie:
        logger.debug("remove cookie:"+CONFIG.global_config.cookie_store+auth_cookie)
        rm(authdir+auth_cookie)
    response.status = 200
    response.add_header("Content-type", "application/json")
    response.delete_cookie("AUTH_COOKIE")
    return json.dumps({"result": "success", "login_status": False,"message":message})


@post("/api/auth/new_user/", apply=[jsonp_plugin])
def auth_new_user():
    try:
        data = request.json
        logger.debug(data)
        invite_token = data.get("token")
        email= urllib.unquote(data.get("userid" )).decode('utf8')
        handle = data.get("handle")
        logger.debug(email)
        logger.debug(invite_token)
        logger.debug(handle)
        res = c.execute("SELECT user_token FROM sxsw_users WHERE invite_token=? AND email=?", (invite_token, email))
        res = c.fetchone()
        logger.debug(res)
        if res:
            my_uuid = unique_id()
            logger.debug("uuid:" + my_uuid)
            c.execute(
                "UPDATE sxsw_users SET invite_token=NULL,invite_created=0,active=1,handle=? WHERE hash IS NULL AND invite_token=? AND email=?",
                (handle, invite_token, email))
            conn.commit()
            c.execute("SELECT * FROM sxsw_users WHERE email=?",(email,))
            logger.debug(c.fetchone())
            result = set_login_cookie(my_uuid, res["user_token"])
            return result

        else:
            return logout("token expired?")
    except:
        logger.exception("er")\

#
# @post("/xapi/auth/new_user/", apply=[jsonp_plugin])
# def auth_new_user():
#     try:
#         data = request.json
#         logger.debug(data)
#         invite_token = data.get("token")
#         email= urllib.unquote(data.get("userid" )).decode('utf8')
#         passwd = data.get("new_password")
#         handle = data.get("handle")
#         hash = pwd_context.encrypt(passwd)
#         logger.debug(hash)
#         logger.debug(email)
#         logger.debug(invite_token)
#         res = c.execute("SELECT user_token FROM sxsw_users WHERE invite_token=? AND email=?", (invite_token, email))
#         res = c.fetchone()
#         logger.debug(res)
#         if res:
#             expires = (datetime.today() + timedelta(minutes=3600)).strftime('%H:%M:%S-%a/%d/%b/%Y')
#             my_uuid = unique_id()
#             logger.debug("uuid:" + my_uuid)
#             c.execute(
#                 "UPDATE sxsw_users SET hash=?,invite_token=NULL,invite_created=0,active=1,handle=? WHERE hash IS NULL AND invite_token=? AND email=?",
#                 (hash, handle, invite_token, email))
#             conn.commit()
#             c.execute("SELECT * FROM sxsw_users WHERE email=?",(email,))
#             logger.debug(c.fetchone())
#             result = set_login_cookie(my_uuid, res["user_token"])
#             return result
#
#         else:
#             return logout()
#     except:
#         logger.exception("er")




# @post("/xapi/auth/login/", apply=[jsonp_plugin])
# def auth_login():
#     try:
#         auth_cookie = request.get_cookie('AUTH_COOKIE')
#         logger.debug(auth_cookie)
#         data = request.json
#         if data and "userid" in data and "password" in data:
#             userid = data["userid"]
#             passwd = data["password"]
#             logger.debug(userid)
#             c.execute("SELECT * FROM sxsw_users WHERE email=? AND active=1", (userid,))
#             res = c.fetchone()
#             logger.debug(res)
#             if res and res["hash"]:
#                 logger.debug("user exists")
#                 testpw = pwd_context.verify(passwd, res["hash"])
#                 if testpw:
#                     if res["uuid"] and len(res["uuid"]) > 0:
#                         my_uuid = res["uuid"]
#                         pass
#                     else:
#                         my_uuid = unique_id()
#                         logger.debug("uuid:" + my_uuid)
#                     return set_login_cookie(my_uuid, res["user_token"])
#                 else:
#                     logger.debug("wrong pw")
#         logger.error("not a valid login request")
#         # else remove cookie
#         if auth_cookie:
#             rm(authdir + auth_cookie)
#         logger.debug("error in auth, logout")
#         response.status = 200
#         response.add_header("Content-type", "application/json")
#         response.delete_cookie("AUTH_COOKIE")
#         return json.dumps(
#             {"result": "failed", "login_status": False, "Location": loginpage + "?error=wrong_credentials"})
#     except:
#         logger.exception("error")
#         response.status = 501
#         return "Internal server error"

@post("/api/auth/reset_password/")
def auth_resetpw():
    try:
        data = request.json
        logger.debug(data)
        token = data.get("token" )
        email= urllib.unquote(data.get("userid" )).decode('utf8')
        logger.debug(email)
        logger.debug(token)
        c.execute("SELECT user_token FROM sxsw_users WHERE reset_token=? AND email=? ",(token,email))
        logger.debug("SELECT user_token FROM sxsw_users WHERE reset_token=%s AND email=%s AND reset_date > date('now','10 minutes')",(token,email))
        res = c.fetchone()
        logger.debug(res)
        if res:
            my_uuid = unique_id()
            logger.debug("uuid:"+my_uuid)
            c.execute("UPDATE sxsw_users SET reset_token=NULL,reset_date=NULL,active=1 WHERE reset_token=? AND email=?",(token,email))
            conn.commit()
            return set_login_cookie(my_uuid,res["user_token"])
            return
        else:
            return logout()
    except:
        logger.exception("er")


@post("/api/auth/logout/", apply=[jsonp_plugin])
def auth_login():
    try:
        auth_cookie = request.get_cookie('AUTH_COOKIE')
        if auth_cookie:
            rm(authdir + auth_cookie)
        logger.debug("error in auth, logout")
        response.status = 200
        response.add_header("Content-type", "application/json")
        response.delete_cookie("AUTH_COOKIE")
        return json.dumps(
            {"result": "ok", "login_status": False})
    except:
        logger.exception("error")
        response.status = 501
        return "Internal server error"

def rm(fname, times=None):
    try:
        os.remove(fname)
    except:
        logger.debug("file "+fname+ " not found")


def set_login_cookie(my_uuid, user_token):
    c.execute("UPDATE sxsw_users SET uuid=?, last_login=date('now') WHERE user_token=?", (my_uuid, user_token))
    conn.commit()
    touch(authdir + my_uuid)
    #expires = (datetime.today() + timedelta(days=1000)).strftime('%H:%M:%S-%a/%d/%b/%Y')
    expires = (datetime.today() + timedelta(days=1000)).strftime('%a, %d %b %Y %H:%M:%S')
    set_cookie_val = "AUTH_COOKIE=%s; Domain=%s; Path=/; Expires=%s" % (my_uuid, cookiedomain, expires)
    logger.debug(set_cookie_val)
    #                start_response("301 Moved Permanently",[("Location",CONFIG.webserver.index),("Content-type", "text/html"),("Set-Cookie",str(set_cookie_val))])
    response.status = 200
    #    response.add_header("Location",CONFIG.webserver.index)
    response.add_header("Content-type", "application/json")
    response.add_header("Set-Cookie", str(set_cookie_val))
    logger.debug("login ok, redirect to index")
    return {"result": "ok", "login_status": True, "Location": homepage}


@post("/api/users/invite/")
def admin_users():
    user = check_user()
    if user:
        logger.debug("test")
        # user = check_admin_rights(request.get_cookie("AUTH_COOKIE"))
        data = request.json
        logger.debug(data)
        email = test_email(data["new_email"])
        if not (email):
            return {"result": "invalid email", "message": "Ongeldig email adres"}

        invite_token = unique_id()
        user_token = unique_id()
        csrf_token = unique_id()
        # check email
        try:
            print (email, user_token, invite_token, csrf_token)
            new_id = c.execute(
                "INSERT INTO sxsw_users (email,user_token,invite_token,csrf_token,invite_created) VALUES (?,?,?,?,date('now'))",
                (email, user_token, invite_token, csrf_token))
            conn.commit()
            send_simple_message(email, invite_token, "mail_invite", "new_user.html","SXSW browser invite")
            #     res = user_list()
            return {"result": "ok", "data": ""}
        except:
            logger.exception("duplicate user")
            return {"result": "duplicate user", "message": "Er is al een gebruiker met dit email adres"}
    return {"result":"failed","message":"not logged in"}

@post("/api/auth/forgot/")
def auth_forgot():
    try:
        auth_cookie = request.get_cookie('AUTH_COOKIE')
        if auth_cookie:
            logger.debug("logout user:"+auth_cookie)
            rm(authdir+auth_cookie)
        logger.debug(auth_cookie)

        data = request.json
        logger.debug(data)
        userid = data.get("userid")
        if userid:
            logger.debug("userid:"+str(userid))
            c.execute("SELECT * from sxsw_users WHERE email=? AND active=1",(userid.lower(),))
            res = c.fetchone()
            logger.debug(res)
            if res:
                logger.debug("user exists")
                reset_token = str(unique_id())
                try:
                    send_simple_message(res["email"],reset_token,"mail_resetpw","reset_password.html","SXSW browser login link")
                except:
                    logger.error("error in sending mail")
                c.execute("UPDATE sxsw_users SET reset_token=?,reset_date=date('now') WHERE email=?",(reset_token,res["email"]))
                conn.commit()
                c.execute("SELECT * FROM sxsw_users WHERE email=?",(res["email"],))
                logger.debug(c.fetchone())
                return {"result":True,"message":"Check your mailbox!"}
    #        start_response("301 Moved Permanently",[("Location","http://bb.gbme.nl/static/ajax/login.html?error=wrong_credentials"),("Content-type", "text/html"),("Set-Cookie","AUTH_COOKIE=no_access; Domain=.gbme.nl; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT")])
            response.delete_cookie("AUTH_COOKIE")
            logger.debug("no such user:"+userid)
            return {"result":True,"message":"check mailbox"}
    except:
        logger.exception("error")
        response.status = 501
        return "Internal server error"


logger.debug("starting server at:" + str(port))

run(host='localhost', port=port)



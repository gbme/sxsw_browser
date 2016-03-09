from bottle import route, post, delete, get, run, template, request, redirect, response, static_file
import requests
import json
from datetime import datetime, timedelta
import log
import uuid
import urllib
logger = log.setup('root', 'sxsw_slack.log')


port = 8082

import time
from slackclient import SlackClient

token = "xoxb-22733755281-DzNcWfVNK7CHibS59Al5m2yW"      # found at https://api.slack.com/web#authentication
sc = SlackClient(token)
print sc.api_call("api.test")
#print sc.api_call("channels.info", channel="1234567890")
#print sc.api_call(
##    "chat.postMessage", channel="#bottest", text="Hello from Python! :tada:",
#    username='pybot', icon_emoji=':robot_face:'
#)


#if sc.rtm_connect():
#    while True:
#        response =  sc.rtm_read()
#        if len(response):
#            for item in response:
#                print item
#                if item.get("type")=="message" and not(item.get("username")=="sxswbot"):
#                    print item["type"]
#                    sc.api_call("chat.postMessage", channel="#bottest", text=item["text"],username='sxswbot', icon_emoji=':robot_face:')
#        time.sleep(1)
#else:
#    print "Connection Failed, invalid token?"



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
@post("/")
def slack_command():
    try:
        fields = ["token",
                    "team_id",
                    "team_domain",
                    "channel_id",
                    "channel_name",
                    "user_id",
                    "user_name",
                    "command",
                    "text",
                    "response_url"]
        data = {}
        for field in fields:
            data[field] = request.forms.getunicode(field)
        words = data.get("text","").split(" ")
        if data.get("command") == "/sxsw" and words[0] == "now":
            r = requests.get("http://127.0.0.1:9200/sxswevents/event/_search?q=attendees:" + data.get("user_name","") + "&sort=utime_start:asc&size=1")
            if r.status_code == 200:
                events = json.loads(r.content)
                logger.debug(events)
                event_source = events.get("hits").get("hits")[0].get("_source")
                responsedata = {
                    "text": "@"+data.get("user_name")+" Your next event:",
                    "attachments": [
                        {
                            "title": event_source.get("title"),
                            "title_link": "http://schedule.sxsw.com/events/"+event_source.get("eventid"),
                            "text": "Time: "+event_source.get("time_raw")+"\nLocation: "+event_source.get("venue_name")+" "+event_source.get("detail_room")
                        }
                        ]

                    }
                r = requests.post(data.get("response_url"),data = json.dumps(responsedata))
                print r.status_code
                print r.content
        
            else:
                logger.debug(r.status_code)
                logger.debug(r.content)
        if data.get("command") == "/sxsw" and words[0] == "search":
            r = requests.get("http://127.0.0.1:9200/sxswevents/event/_search?q=searchdata:" + "+".join(words[1:]) + "&sort=utime_start:asc&size=20")
            if r.status_code == 200:
                response_text = ""
                events = json.loads(r.content)
                logger.debug(events)
                event_attachments = []
                events = events.get("hits").get("hits")
                if len(events):
                    for event in events:
                        event_source = event.get("_source")
                        event_attachments.append({
                                "title": event_source.get("title"),
                                "title_link": "http://schedule.sxsw.com/events/"+event_source.get("eventid"),
                                "text": "Time: "+event_source.get("date_raw")+ " " + event_source.get("time_raw")+"\nLocation: "+event_source.get("venue_name")+" "+event_source.get("detail_room")
                            })
                    response_text = "@"+data.get("user_name")+" Search results for: \"" +" ".join(words[1:]) +"\""
                else:
                    response_text = "@"+data.get("user_name")+" No results for: \"" +" ".join(words[1:]) +"\""
                responsedata = {
                        "text": response_text ,
                        "attachments": event_attachments
                        }
                r = requests.post(data.get("response_url"),data = json.dumps(responsedata))
                print r.status_code
                print r.content
        
            else:
                logger.debug(r.status_code)
                logger.debug(r.content)
        logger.debug(data)
    except:
        logger.exception("error")
        response.status = 501
        return "Internal server error"



logger.debug("starting server at:" + str(port))

run(host='localhost', port=port)



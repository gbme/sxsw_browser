import requests
from requests.auth import HTTPBasicAuth
import json
import os
from os import path

import log
logger = log.setup('root','importer.log')
import os.path

elastic_url = "https://756c32bb9a4eee771afad6fcea3d0b33.us-east-1.aws.found.io:9243"
store_url = "http://127.0.0.1:8081"

auth = HTTPBasicAuth('readwrite', 'nnanpq356kmlohlfjg')
headers = {'Content-type': 'application/json', "authtoken":"gbme"}
class DecimalEncoder(json.JSONEncoder):
#    def totimestamp(self, dt, epoch=datetime(1970,1,1)):
#        td = dt - epoch
#        # return td.total_seconds()
#        return int(((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e3)+(CONFIG.global_config.timezone_offset*3600000))


    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isintance(o,bool):
            if o: return 1
            return 0
        if isinstance(o, datetime):
            return self.totimestamp(o)
        return super(DecimalEncoder, self).default(o)


def reset():
    logger.debug( "delete:"+"elastic/messages")
    d = requests.delete(elastic_url+"/sxswevents/",headers=headers,auth=auth)
    logger.debug(d.text)
    logger.debug("result for elastic delete:"+str(d.status_code))
    data = {
  "mappings": {
    "sxswevent": {
      "_all":       { "enabled": False  },
      "properties":
          {
            "status":            { "type": "string"  },
            "title":            { "type": "string"  },
            "rsvp":            { "type": "boolean"  },
            "venue_name":       { "type": "string" , "analyzer" : "keyword"  },
            "description":      { "type": "string"  },
            "event-image":      { "type": "string"  },
            "eventtype":        { "type": "string"  , "analyzer" : "keyword" },
            "track":            { "type": "string" , "analyzer" : "keyword"  },
            "format":           { "type": "string" , "analyzer" : "keyword"  },
            "url":              { "type": "string"  },
            "date_raw":         { "type": "string" , "analyzer" : "keyword"  },
            "time_raw":         { "type": "string" , "analyzer" : "keyword"  },
            "utime_start":      { "type": "date" },
            "tags":             { "type": "string" , "analyzer" : "keyword"  },
            "detail_room":      { "type": "string", "analyzer" : "keyword"  },
            "level":            { "type": "string", "analyzer" : "keyword"  },
            "attendees":             { "type": "string" , "analyzer" : "keyword"  },

            "presenters": {
                "type": "object" ,
                "properties" :
                {
                    "name":     {"type":"string" , "analyzer" : "keyword"}  ,
                    "title":    {"type":"string" , "analyzer" : "keyword"}  ,
                    "company":  {"type":"string" , "analyzer" : "keyword" }  ,
                }
            },
      }
    }

}
}
    d = requests.put(elastic_url+"/sxswevents/",headers=headers, data=json.dumps(data),auth=auth)
    logger.debug(d.text)
    logger.debug("result for elastic:"+str(d.status_code))

#    body = {
#        "sxswevent" : {
##            "properties" : {
#                "description" : {"type" : "string","store":True },
#                "sensor_code":{"type":"string","store":True},
#                "image":{"type":"string","store":True}
#            }
#        }
#    }
#    d = requests.put("https://test.gbme.nl/elastic/messages/_mapping/message",headers=headers,data=json.dumps(body))
#    print(d.text)
#    print("result for elastic:"+str(d.status_code))

def get_users_for_event(eventid):
    r = requests.get(store_url+"/events/"+eventid+"/users/")
    data = json.loads(r.content)
    logger.debug( data )
    res = []
    for a in data:
        res.append(a["userid"])
    return res

def fill():
    files = os.listdir("/vagrant/data/")
    for file in files:
        try:
            filename = "/vagrant/data/"+file
            oldfilename = "/vagrant/data_old/"+file
            f = open(filename,"r")
            _d = f.read()
            data = json.loads(_d)
            f.close()
            data_old = False
            if os.path.isfile(oldfilename):
                f = open(oldfilename,"r")
                _d = f.read()
                data_old = json.loads(_d)
                f.close()

            if not(data_old):  
                data["status"] = "new"
            else:
                if data == data_old:
#                    data["status"] = "existing"
                    pass
                else:
                    data["status"] = "changed"
            data["searchdata"] = data["title"]+data["description"]+str(data["tags"])+str(data["presenters"])
            d = requests.put(elastic_url+"/sxswevents/event/"+file  ,data=json.dumps(data,cls=DecimalEncoder),headers=headers,auth=auth)
            logger.debug(d.status_code)
            logger.debug( d.content )
        except Exception:
            logger.exception( "error" )


def read():
    d = requests.get("https://3afa1f36fdbff028682948a78d079ec7.eu-west-1.aws.found.io:9243/_cat/indices" ,auth=auth)
    print d.status_code
    print d.content


def main():
    read()
main()
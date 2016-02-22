import requests
import json
from datetime import datetime

url = "http://127.0.0.1/elastic/sxswevents/event/_search?q=attendees:gerbrand&sort=utime_start:asc&size=200"


def test_all():
    r = requests.get(url)
    data = json.loads(r.content)
    for a in data["hits"]["hits"]:
        res = a["_source"]
        timestring = res["date_raw"] + " 2016 " + (res["time_raw"]).split(" - ")[0].replace(" ", "0")
        print timestring
        date_object = datetime.strptime(timestring, '%A, %B %d %Y %H:%M%p')
        utime_start = int(date_object.strftime("%s")) * 1000
        print res["date_raw"] + res["time_raw"] + "\t" + str(res["utime_start"]) + "\t" + str(utime_start)

test_all()


for s in ["Friday, March 11 2016 11:00AM","Friday, March 11 2016 02:00PM"]:
    print s
    date_object = datetime.strptime(s, '%A, %B %d %Y %I:%M%p')
    print date_object

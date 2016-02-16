from lxml import html
import requests
import json
import os
from datetime import datetime
import time
event_baseurl = "http://schedule.sxsw.com/2016/events/"
import log
logger = log.setup('root','scraper.log')
import subprocess

evenids = []


def clean_text(t):
    return t.replace("\n","")



def get_presenters(event):
    presenters = []
    for presenter in event.xpath("//div[@class='presenter-area']/div/hgroup"):
        t = {}
        t["name"] = get_first(presenter.xpath("h4[@class='pres_name']/text()"))
        t["title"] = get_first(presenter.xpath("*[@class='pres_title']/text()"))
        t["company"] = get_first(presenter.xpath("*[@class='pres_company']/text()"))
        presenters.append(t)
    return presenters

def get_first(ar):
    return (ar[0] if len(ar)>0 else "").encode('utf-8')

failed = []

def get_event(eventid):
    try:
        url = event_baseurl+eventid
        logger.debug( url)
        print url
        r = requests.get(url,timeout=1)
        res = {}
        event = html.fromstring(r.content)
        res["rsvp"] = r.content.find("RSVP") > -1
        res["eventid"] = eventid
        res["title"]  = get_first(event.xpath("//div[@class='title']/h1/text()")).replace("\n","")
        res["date_raw"] = get_first(event.xpath("//div[@id='detail_time']/p/b/text()"))
        res["time_raw"] = event.xpath("//div[@id='detail_time']/p/text()")[2].replace("\n","")
        timestring = res["date_raw"]+" 2016 " +(res["time_raw"]).split(" - ")[0].replace(" ","0")
        date_object = datetime.strptime(timestring, '%A, %B %d %Y %H:%M%p')
        res["utime_start"] = int(time.mktime(date_object.timetuple()))*1000
        res["venue_url"] = get_first(event.xpath("//a[@class='detail_venue']/@href"))
        res["detail_room"] = get_first(event.xpath("//span[@class='detail_room']/text()"))
        res["description"] = get_first(event.xpath("//div[@class='block description']/p/text()"))
        res["venue_name"] = clean_text( event.xpath("//a[@class='detail_venue']/text()")[0])
        res["format"] = get_first(event.xpath("//div[@class='block' and ./span/text()='Format']/div/a/text()"))

        res["event-image"] = get_first(event.xpath("//div[@class='event-image']/img/@src"))
        res["eventtype"] = get_first(event.xpath("//div[@class='block' and ./span/text()='Event Type']/div/text()")).replace("\n","")
        res["track"] = get_first(event.xpath("//div[@class='block' and ./span/text()='Track']/a/text()")).replace("\n","")
        res["level"] = get_first(event.xpath("//div[@class='block' and ./span/text()='Level']/div/text()")).replace("\n","")
        tags = event.xpath("//div[@class='block' and ./span/text()='Tags']/div/a")
        res["url"] = get_first(event.xpath("//div[@class='details']/div[ ./span/text()='Online']/a/@href"))

        res["tags"] = []
        for tag in tags:
            res["tags"].append(tag.text)
        res["presenters"] = get_presenters(event)
        filename = '/vagrant/data/'+eventid+'.json'
        if os.path.isfile(filename):
            os.remove(filename)
        f = open(filename, 'wc')
        f.write(json.dumps(res))
        f.close()
    except:
        logger.exception("err")
        failed.append(eventid)


def main():
    subprocess.call("rm /vagrant/data_old/*;mv /vagrant/data/* /vagrant/data_old/", shell=True)    
    for day in [11,12,13,14,15]:
        r = requests.get("http://schedule.sxsw.com/?day="+str(day)+"&conference=interactive")
        tree = html.fromstring(r.content)
        links = tree.xpath('//div[@class="bar interactive"]')
        for link in links:
            eventid = link.get("id").split("cell_")[1]
            get_event(eventid)
        for eventid in failed:
            get_event(eventid)
            



        pass

main()

#get_event("event_PP51607")
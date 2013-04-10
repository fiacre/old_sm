#!  /usr/bin/python

import BeautifulSoup
import urllib2
import getopt, sys, os
import re
import urllib2
from urllib2 import URLError, HTTPError
import socket
from BeautifulSoup import BeautifulSoup
from xml.sax.handler import ContentHandler
import xml.sax
from glob import glob
socket.setdefaulttimeout(20)
from Cheetah.Template import Template

class urlScraper (object) :

    def __init__ (self, url):
        self.url = url


    def _check_for_redirect(self, url):
        user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"
        headers = { "User-Agent" : user_agent }
        req = urllib2.Request(self.url, None, headers)
       
        real_url = response.geturl()
        try :
            urllib2.urlopen(req)
        except URLError, e:
            print >>sys.stderr, str(e)

        return real_url

    def do_fetch(self, url) :
        user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"
        headers = { "User-Agent" : user_agent }
        req = urllib2.Request(self.url, None, headers)
        try :
            urllib2.urlopen(req)
        except URLError, e:
            if hasattr(e, "reason") :
                print e.reason
            #sys.exit(1)

        try :
            response = urllib2.urlopen(req)
        except HTTPError, e:
            if hasattr(e, 'code'):
                print "The server couldn't fulfill the request."
                print 'Error code: ', e.code
            #sys.exit(1)

        html = response.read()
        #print "got html\n\n"
        return html

    def scrape_html_generator (self, html) :
        href_re = re.compile(r'href="(.*\.photogallery)"')
        #photogallery = re.compile(r'.*href=\"(\/.*\.photogallery)\".*')
        soup = BeautifulSoup(html)
        for d in soup.findAll(id="module-related-links"):
            for link in d.findAll ('a'):
                #print link
                #print str(link)
                m = href_re.search(str(link))
                if m:
                    #print "Cool!"
                    yield "http://www.chicagotribune.com" + m.group(1)
        return

class rssDataManager (object):
    def __init__(self, url):
        self.url = url
        self.soup = BeautifulSoup(self.html)
        self.url_scraper = urlScraper(self.url)

    def getKeys (self) :
        data = {}
        html = do_fetch( url )
        links = {}
        for link in scrape_html_generator(html):
            links[link] = 1

        for link in links.keys() :
            for image in image_gallery_generator(link, 5):
                print link
                for i in image:
                    print "%s : %s" % ( str(i[0]).encode('ascii'), str(i[1]).encode('ascii') )
                    data[str(i[0]).encode('ascii')] = str(i[1]).encode('ascii')
                    render_template (data)

    def image_gallery_generator ( self, link, max ) :
        for i in range(1,max):
            a_link = link + "?index=%s" % i
            #print a_link 
            html = do_fetch(a_link)
            soup = BeautifulSoup(html)
            for image in soup.findAll("img", { "class" : "gallery-slideshow-photo" }):
                #print "Ga Ga!"
                yield image.attrs
        return
        
    def render_template (self) :
        for k, v in d.iteritems():
            print k, v

    def parse_feeds(self):
        #feeds = ["http://chicagosports.chicagotribune.com/sports/mobilefeed.xml", "http://www.chicagotribune.com/sports/mobilefeed.xml"] 
        feeds = [
        "http://chicagosports.chicagotribune.com/sports/mobilefeed.xml", 
        "http://www.chicagotribune.com/sports/mobilefeed.xml", 
        "data/mobilefeed.xml"
        ] 
        parser = xml.sax.make_parser()
        handler = SportsFeedHandler()
        parser.setContentHandler(handler)
        #parser.parse("./data/mobilefeed.xml")
        for feed in feeds :
            parser.parse(feed)
            #mapping = handler.mapping.keys()
            #mapping.sort()
            #for i, k in ( handler.data, handler.mapping.keys() ):
            #    print k, i
            #for k, v in handler.mapping.iteritems():
                #print k, v
                #print mapping
                #for k, v in i.handler.maping.iteritems() :
                #    print k, v


class SportsFeedHandler (ContentHandler):
    def __init__(self) :
        self.data = []
        self.mapping = {}
        self.in_item = 0
        self.in_url = 0
        self.in_titleline = 0
        self.in_date = 0
        self.date = self.titleline = self.url = ""
    
    def startElement (self, name, attr) :
        if name == 'item':
            self.in_item = 1
            #item_id = attr.getValue("id")
            self.mapping['item_id'] = attr.getValue("id")
        elif name == 'url':
            self.in_url = 1
            self.url = ""
        elif name == 'date':
            self.in_date = 1
            self.date = ""
        elif name == 'titleline':
            self.in_titleline = 1
            self.titleline = ""


    #def handleContent (self, data):
    def characters (self, data):
        #print data
        if self.in_titleline:
            self.titleline += data
        elif self.in_url:
            self.url += data
        elif self.in_date:
             self.date += data
        

    def endElement (self, name):
        if name == 'url':
            self.in_url = 0
            self.mapping['item_url'] = self.url
        elif name == 'item':
            self.in_item = 0
            self.data.append(self.mapping['item_id'])
            self.data.append(self.mapping['item_url'])
            self.data.append(self.mapping['item_titleline'])
            self.data.append(self.mapping['item_date'])
            self.titleline = self.url = self.date = ""
            for k, v in self.mapping.iteritems() :
                print "{ %s : %s }" % ( k, v )
        elif name == 'titleline':
            self.in_titleline = 0
            self.mapping['item_titleline'] = self.titleline
        elif name == 'date':
            self.in_date = 0
            self.mapping['item_date'] = self.date



class templateWriter (object):
    class RssChannel (object) :
        def __init__ (self, title, link, desc):
            self.title = title
            self.link = link
            self.desc = desc
    class RssItem (object):
        def __init__ (self, guid, link, title, images = [] ):
            self.images = images
            self.guid = guid
            self.link = link
            self.title = title

    class RssImage (object):
        def __init__(self, url, title, desc, height = 0, width = 0):
            self.url = url
            self.title = title
            self.desc = desc
            self.height = height
            self.width = width
    
    class RssEntry (object):
        def __init__(self, rss_channel, rss_item, rss_image):
            self.rss_channel = rss_channel
            self.rss_item = rss_item
            self.rss_image = rss_image

    def write_template (self):
        entries = []
        rss_channel = RssChannel( "this is a title", "this is a link", "this is a dec")
        rss_item = RssItem( 12345, "this is a link", "Here's the title", ["this is an image 1", "this is an image 2"])
        rss_image_a = RssImage ("http://www.foo.bar/image.jpg", "Foo and Bar", "an image of Foo and Bar")
        rss_image_b = RssImage ("http://www.foo.blah/abc_image.jpg", "Foo not Bar", "an image of Foo not Bar")

        entries.append(RssEntry(rss_channel,rss_item,rss_image_a))
        entries.append(RssEntry(rss_channel,rss_item,rss_image_b))
    
        template_file = "images.tmpl"
        template = Template(
            file = template_file,
            searchList = [
            { "channel_title" : rss_channel.title,
              "channel_link" : rss_channel.link,
              "channel_desc" : rss_channel.desc,
              "item_guid" : rss_item.guid,
              "item_link" : rss_item.link,
              "item_title" : rss_item.title,
              "item_images" : [rss_image_a, rss_image_b]
            } ] 
        )

        print str(template)




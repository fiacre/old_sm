#!  /usr/bin/python
from xml.sax.handler import ContentHandler
import xml.sax
import urllib2
import getopt, sys, os
import re
from urllib2 import URLError, HTTPError
import socket
from BeautifulSoup import BeautifulSoup
import ConfigParser
from Cheetah.Template import Template

from PhotoGallery import PhotoGallery
from SportsFeed import SportsFeedHandler

def fetch_photogallery (mapping = {}) :
    
    """
    if ( mapping['item_id']  
            and
            mapping['item_url']
            and
            mapping['item_titleline']
            and
            mapping['item_date']
        ):
    """
    try:
        pg = PhotoGallery( mapping['item_id'], mapping['item_url'], mapping['item_titleline'], mapping['item_date'] )
        pg.get_photogallery_urls()
    except KeyError, e:
        print str(e)
        mapping['item_titleline'] = "Chicago Sports"
        pg = PhotoGallery( mapping['item_id'], mapping['item_url'], mapping['item_titleline'], mapping['item_date'] )
        pg.get_photogallery_urls()

feeds = [
    "http://chicagosports.chicagotribune.com/sports/mobilefeed.xml", 
    "http://www.chicagotribune.com/sports/mobilefeed.xml" 
]
parser = xml.sax.make_parser()
handler = SportsFeedHandler()
parser.setContentHandler(handler)

for feed in feeds :
    parser.parse(feed)
    for elem in handler.feed_array:
        fetch_photogallery ( elem )
        print "DEBUG: Feed Array : %r " % elem
        #for k, v in  i.iteritems():
        #    print k, v


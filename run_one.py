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
    pg = PhotoGallery( mapping['item_id'], mapping['item_url'], mapping['item_titleline'], mapping['item_date'] )
    pg.get_photogallery_urls()


#mapping = { "item_id" : "41123601", 
# "item_titleline" : "Tribune staff reporter",
#  "item_url" : "http://chicagosports.chicagotribune.com/sports/baseball/whitesox/cs-080720-chicago-white-sox-kansas-city-royals,1,3807723.story",
#   "item_date" : "2008-07-20" }

mapping = { "item_id" : "41147917", 
 "item_titleline" : "Tribune staff reporter",
  "item_url" : "http://www.chicagotribune.com/sports/cs-080721-jermaine-dye-knee-white-sox,0,5385812.story",
   "item_date" : "2008-07-22" }

fetch_photogallery ( mapping )
print "DEBUG: Feed Array : %r " % mapping

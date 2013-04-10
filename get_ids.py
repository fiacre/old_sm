#!  /usr/bin/python

from xml.sax.handler import ContentHandler
import xml.sax
from glob import glob
import sys

class SportsFeedHandler (ContentHandler):
    def __init__(self) :
        self.data = []
        self.feed_array = []
        self.mapping = {}
        self.in_item = 0
        self.in_url = 0
        self.in_titleline = 0
        self.in_date = 0
        self.date = self.titleline = self.url = ""
        self.have_item_id = self.have_item_url = self.have_item_date = self.have_title_line = 0
    
    def startElement (self, name, attr) :
        if name == 'item':
            self.in_item = 1
            self.have_item_id = 1
            #item_id = attr.getValue("id")
            self.mapping['item_id'] = attr.getValue("id")
        elif name == 'url':
            self.in_url = 1
            self.have_item_url = 1
            self.url = ""
        elif name == 'date':
            self.in_date = 1
            self.have_item_date = 1
            self.date = ""
        elif name == 'titleline':
            self.in_titleline = 1
            self.have_title_line = 1
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
            #self.feed_array.append(self.mapping)
            if ( self.have_item_id == 1 and self.have_item_url == 1
                and self.have_item_date == 1 and self.have_title_line ==1):
                self.feed_array.append( { "item_id" : self.mapping['item_id'],
                                "item_url" : self.mapping['item_url'],
                                "item_timeline" : self.mapping['item_titleline'],
                                "item_date" : self.mapping['item_date'] } )
            elif ( self.have_item_id == 1 and self.have_item_url == 1 and self.have_item_date == 1 ) :
                self.feed_array.append( { "item_id" : self.mapping['item_id'],
                    "item_url" : self.mapping['item_url'],
                    "item_date" : self.mapping['item_date'],
                    "item_timeline" : "Chicago Sports" } )
            print
            #self.item_generator ( self.mapping )
            for k, v in self.mapping.iteritems() :
                print "{ %s : %s }" % ( k, v )
            self.titleline = self.url = self.date = ""
            self.have_item_id = self.have_item_url = self.have_item_date = self.have_title_line = 0
            self.mapping = {}
        elif name == 'titleline':
            self.in_titleline = 0
            self.mapping['item_titleline'] = self.titleline
        elif name == 'date':
            self.in_date = 0
            self.mapping['item_date'] = self.date

    #def item_generator (self, map = {}) :
    #    for k, v in map.iteritems() :
    #        yield "{ %s : %s }" % ( k, v ) 
    #    return

def main():
    #feeds = ["http://chicagosports.chicagotribune.com/sports/mobilefeed.xml", "http://www.chicagotribune.com/sports/mobilefeed.xml"] 
    feeds = [
        "http://www.chicagotribune.com/sports/mobilefeed.xml", 
        "http://chicagosports.chicagotribune.com/sports/mobilefeed.xml" 
    ] 
    parser = xml.sax.make_parser()
    handler = SportsFeedHandler()
    parser.setContentHandler(handler)
    #parser.parse("./data/mobilefeed.xml")
    for feed in feeds :
        parser.parse(feed)
        #for col in handler.item_generator():
        #    print col
        for i in handler.feed_array:
            for k, v in  i.iteritems():
                print k, v
        #    for k,v in i.iteritems():
        #        print k, v
        #mapping = handler.mapping.keys()
        #mapping.sort()
        #for i, k in ( handler.data, handler.mapping.keys() ):
        #    print k, i
        #for k, v in handler.mapping.iteritems():
            #print k, v
            #print mapping
            #for k, v in i.handler.maping.iteritems() :
            #    print k, v



if __name__ == "__main__" :
    main()



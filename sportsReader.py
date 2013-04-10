#!  /usr/bin/python

import urllib2
from urllib2 import URLError, HTTPError
import socket
from BeautifulSoup import BeautifulSoup
import sys
import re
from Cheetah.Template import Template
from xml.sax.handler import ContentHandler
import xml.sax


## for debugging
import pdb


def do_fetch(url, output_file = None) :
    """ handy url grabber function 
        raises error and exits on URLError or HTTPError
    """
    user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"
    headers = { "User-Agent" : user_agent }
    req = urllib2.Request(url, None, headers)
    try :
        urllib2.urlopen(req)
    except URLError, e:
        if hasattr(e, "reason") :
            print e.reason
        sys.exit(1)

    try :
        response = urllib2.urlopen(req)
    except HTTPError, e:
        if hasattr(e, 'code'):
            print "The server couldn't fulfill the request."
            print 'Error code: ', e.code
        sys.exit(1)

    url_data = response.read()
    #return html
    if output_file == None:
        return url_data
    else:
        try:
            #f = open("%s/output_file", "wb") % ("/home/webadmin/scrollmotion.virtual.vps-host.net/html/xml/chicagotribunesportsreader/images")
            filename = "./tmp/images" + output_file
            f = open(filename, "wb")
            f.write(url_data)
            f.close()
        except IOError, e:
            #raise IOError, e
            print >>sys.stderr, "Could not open %s for writing! %s" % (output_file, e)

class SportsFeedHandler (ContentHandler):
    """
    class SportsFeedHandler
    extends xml.sax.handler.ContentHandler
    """

    def __init__(self) :
        #self.data = []
        self.feed_array = []
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
            ## on close of item tag -- take the mapping and append it to
            ## the data array
            #self.in_item = 0
            #self.data.append(self.mapping['item_id'])
            #self.data.append(self.mapping['item_url'])
            #self.data.append(self.mapping['item_titleline'])
            #self.data.append(self.mapping['item_date'])
            #self.titleline = self.url = self.date = ""
            #print
            #for k, v in self.mapping.iteritems() :
            #    print "{ %s : %s }" % ( k, v )
            self.feed_array.append(self.mapping)
        elif name == 'titleline':
            self.in_titleline = 0
            self.mapping['item_titleline'] = self.titleline
        elif name == 'date':
            self.in_date = 0
            self.mapping['item_date'] = self.date


class PhotogalleryData (object):
    """
    class PhotogalleryData
    takes the URLs of stories scraped from a feed
    loops over those URLs
    looks for a tag with 'photogallery'
    takes that tag and extracts a URL that has a photogallery
    counts the images in the photogallery
    constructs http://www.chicagotribune.com + photogallery_url + ?index=x
    where is is in the range 1 to #images in the photogallery
    fetches those images
    saves them as date + name
    """
    # private data
    num_images = 0
    gallery_url = ""

    def __init__(self, story_url):
        self.story_url = story_url

    def _how_many_images (self, html_of_photogallery) :
        """ _how_many_images -> integer
            determine the number of images in the photogallery
        """
        # html = do_fetch (self.gallery_url)
        soup = BeautifulSoup(html_of_photogallery)
        # regex to capture MAX number of images ... this may change!!!
        range_re = re.compile(r'(?:Image)*\s\d+ of (\d+)')
        # so far, the info on images is in div id=photo-index
        for d in soup.findAll('div', { 'id' : 'photo-index' } ):
            range_string = d.contents[0].strip()
            m = range_re.match(range_string)
            # if we have a match ... great!
            # set a private var to hold that value
            if m:
                #return m.group(1)
                self.num_images = int(m.group(1))
                return self.num_images
    
    def _get_image_gallery (self, link) :
        """ _get_image_gallery
            take a an image link found in the original sotory scraped from a feed
            we've figured out how many images are in this gallery
            loop over and get them
            prepend the date as yyyy-mm-dd
            save to local disk
        """
        if self.num_images == 0 :
            html_of_photogallery = do_fetch(link)
            max = self._how_many_images(html_of_photogallery)
            if not max > 1 :
                raise ValueError, "Only one image in the gallery!"
        images = []
        for i in range(1, self.num_images):
            a_link = link + "?index=%s" % i
            html_of_photogallery = do_fetch(a_link)
            # is this the first time this generator has been called?
            # if so ... find out how many images are in the photogallery
            if self.num_images == 0 :
                self._how_many_images(html_of_photogallery)
            soup = BeautifulSoup(html_of_photogallery)
            # so far, all gallery images are in a div with class=gallery-slideshow-photo
            for image in soup.findAll("img", { "class" : "gallery-slideshow-photo" }):
                images.append(image.attrs)
        return images
        #images = []
        #return
        
    def _scrape_story_generator (self, html_of_story) :
        # we are looking for a link with 'photogallery' in it
        href_re = re.compile(r'href="(.*\.photogallery)"')
        # parse the original story's html
        soup = BeautifulSoup(html_of_story)
        # look at div elements with related-links id 
        #for d in soup.findAll('div'):
        for d in soup.findAll(id="module-related-links"):
            for link in d.findAll ('a'):
                m = href_re.search(str(link))
                # if our regex matches -- great!  prepend the base URL, yeild it
                if m:
                    yield "http://www.chicagotribune.com" + m.group(1)
        return


    def get_photogallery_urls(self):
        """ get phtogallery location
            we have the URL of the story
            we need the url of the photogallery (if any) in that story
        """
        # how many images are we grabbing?
        # self._how_many_images()
        # we don't want duplictes to stick the img hrefs in a dictionary
        links = {}
        # hold the scaped data in a dictionary
        data = {}
        # since the keys repeat for each image -- we have to aggregate the key,value pairs
        aggregator = []
        # what is the html of the original story we got from the Feed?
        html_of_story = do_fetch(self.story_url)
        # self._how_many_images (self, html_of_photogallery)
        for link in self._scrape_story_generator(html_of_story):
            links[link] = 1
            for link in links.keys() :
                # pull ourselves up by our bootstaps to get number of imges
                # first time though we parse the link twice -- once to get the number of
                # images, then to get the href
                # gotta fix that ....
                image_gallery = self._get_image_gallery(link)
                for images in image_gallery:
                    #print >>sys.stderr, link
                    for i in images:
                        #print "%s : %s" % ( str(i[0]).encode('ascii'), str(i[1]).encode('ascii') )
                        data[str(i[0]).encode('ascii')] = str(i[1]).encode('ascii')
                        aggregator.append(data)
        if aggregator:
            return aggregator
        else: 
            print >>sys.stderr, "Got no image data from the photogallery -- moving on"



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



def scrape_feeds():
    #feeds = ["http://chicagosports.chicagotribune.com/sports/mobilefeed.xml", "http://www.chicagotribune.com/sports/mobilefeed.xml"] 
    accumulator = []
    feeds = [
        "http://chicagosports.chicagotribune.com/sports/mobilefeed.xml", 
        "http://www.chicagotribune.com/sports/mobilefeed.xml" 
    ] 
    parser = xml.sax.make_parser()
    handler = SportsFeedHandler()
    parser.setContentHandler(handler)

    #parser.parse("./data/mobilefeed.xml")

    for feed in feeds :
        parser.parse(feed)
        feed_data = handler.feed_array
        for i in feed_data:
            accumulator.append(i)
    return accumulator

    #        for k,v in i.iteritems():
    #            print k, v


#def gather_image_data(mapping):
     

if __name__ == '__main__':
    ## set_tace for debugging
    #pdb.set_trace()
    rss_data_array = scrape_feeds()
    for i in rss_data_array:
        for k, v in i.iteritems():
            if k == "item_id":
                print k, v
            elif k == "item_titleline": 
                print k, v
            elif k == "item_date":
                print k, v
            elif k == "item_url":
                print k, v
                gallery_data = PhotogalleryData(v)
                image_data = gallery_data.get_photogallery_urls()

                
        
    #gallery_data = PhotogalleryData("http://www.chicagotribune.com/sports/sns-ap-glf-british-open,0,285322.story")
    #gallery_data = PhotogalleryData("http://www.chicagotribune.com/sports/cs-080717-ryan-dempster-chicago-cubs-world-series,0,5879128.story")
    #gallery_data = PhotogalleryData("http://chicagosports.chicagotribune.com/sports/baseball/cubs/cs-080714-ron-santo-1969-all-star-game-mitchell,1,7754823.column")

#        for k, v in i.iteritems():
#            print "key : %s, value %s" % (k, v)



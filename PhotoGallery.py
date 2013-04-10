import urllib2
import getopt, sys, os
import re
from urllib2 import URLError, HTTPError
import socket
from BeautifulSoup import BeautifulSoup
import ConfigParser
from Cheetah.Template import Template


import pdb

socket.setdefaulttimeout(20)

class PhotoGallery (object):
    """
    class PhotoGallery
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
    def __init__ (self, item_id, item_url, item_titleline, item_date):
        self.item_id = item_id
        self.item_url = item_url
        self.item_titleline = item_titleline
        self.item_date = item_date
        self.image_repository = "/home/webadmin/scrollmotion.virtual.vps-host.net/html/xml/chicagotribunesportsreader/images/"
        self.image_location = "http://scrollmotion.virtual.vps-host.net/xml/chicagotribunesportsreader/images/"
        self.xml_path = "/home/webadmin/scrollmotion.virtual.vps-host.net/html/xml/chicagotribunesportsreader/"

    def _check_for_redirect(self, url):
        print "DEBUG: Checking for redirect : %s" % url
        user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"
        headers = { "User-Agent" : user_agent }
        req = urllib2.Request(url, None, headers)
        try :
            response = urllib2.urlopen(req)
        except URLError, e:
            print >>sys.stderr, str(e)
        real_url = response.geturl()
        print "DEBUG: redirect? : %s" % real_url
        return real_url


    def get_photogallery_urls (self) :
        #pdb.set_trace()
        data = {}
        chicago_tribune_base_url = ""
        html_of_story = self.do_fetch(self.item_url)
        url_components = self.item_url.split('/')
        for s in url_components:
            print s
            if s == "chicagosports.chicagotribune.com":
                chicago_tribune_base_url = "http://chicagosports.chicagotribune.com"
            elif s == "www.chicagotribune.com":
                chicago_tribune_base_url = "http://www.chicagotribune.com"

        links = {}
        photo_links = []
        image_properties = {}
        all_images = []
        max_photos = 0
        aggregator = []
        html_of_gallery = ""
        real_photo_gallery_url = ""
        #for link in scrape_story_generator(html):
        # photo_links = self.scrape_story_generator(html_of_story)
        photo_links = self.scrape_story_generator(html_of_story, chicago_tribune_base_url)

        #pdb.set_trace()
        if photo_links:
            real_photo_gallery_url = self._check_for_redirect(photo_links[0])
            if real_photo_gallery_url is not  photo_links[0]:
                print "DEBUG -- given url : %s, real url %s" % (self.item_url, real_photo_gallery_url)
                html_of_gallery = self.do_fetch(real_photo_gallery_url)
            else:
                html_of_gallery = self.do_fetch(photo_links[0])
            print "photo link 0 ++++++++ %s " % photo_links[0]
            print "item url +++++ %s " % self.item_url
            max_photos = self.how_many_images(html_of_gallery)
            if max_photos == 0 or max_photos == None:
                max_photos = self.really_how_many_images(html_of_gallery)
            print  >>sys.stderr, "max photos +++++++++++++++++++++++++++++++ %s " % str(max_photos)
            if max_photos == 0 or max_photos == None:
                print  >>sys.stderr, "can't seem to figure out how many photos in the gallery\n let's get 4"
                max_photos = 4
            # hack to get that last photo
            #max_photos = max_photos+1 
            #print  >>sys.stderr, "max photos +++++++++++++++++++++++++++++++ %s " % str(max_photos)
        else:
            print >>sys.stderr, "Got no image data from the photogallery -- moving on"
            return
            
        #for
        #for link in photo_links:
        #    links[link] = 1
        #    #print link
        ### HACK Attack
        links[real_photo_gallery_url] = 1

        #print "+++++++++++++++++++++++++++++++ %s ++++++++++++++++++++++++++++++++++" % max
        for link in links.keys() :
            for image_attrs in self.image_gallery_generator(link, max_photos):
                #print link
                image_properties = {}
                for i in image_attrs:
                    #print "%s : %s" % ( str(i[0]).encode('ascii'), str(i[1]).encode('ascii') )
                    # http://www.orlandosentinel.com/media/photo/2008-07/41092629.jpg
                    if i[0] == 'src':
                        print "DEBUG: Download this :  %s" % i[1]
                        image_name = i[1].split('/')[-1]
                        image_name = self.item_date + '-' + str(image_name).encode('ascii')
                        print image_name
                        # comment below for testing
                        self.do_fetch(i[1], self.image_repository + image_name)
                        image_properties['src'] = self.image_location + image_name
                        #image_properties
                    elif i[0] == 'alt':
                        print "And this is the title %s" % i[1]
                        image_properties['alt'] = str(i[1]).encode('ascii')
                    elif i[0] == 'height':
                        print "And this is the height %s" % i[1]
                        image_properties['height'] = str(i[1]).encode('ascii')
                    elif i[0] == 'width':
                        print "And this is the width %s" % i[1]
                        image_properties['width'] = str(i[1]).encode('ascii')
                    elif i[0] == 'class':
                        continue
                    
                all_images.append(image_properties)
                #data[str(i[0]).encode('ascii')] = str(i[1]).encode('ascii')
                print "DEBUG: Image Properties : %r" % image_properties
            self.render_template (self.item_id, self.item_url, self.item_titleline, self.item_date, all_images)
            image_properties = {}
            all_images = []
        #print html

    def do_fetch(self, url, output_file = None) :
        if output_file is not None:
            print "++++++++++++++++++++++++++++++++ %s .... " % output_file
            if os.path.exists(output_file):
                "already downloaded %s, skipping" % output_file
                return
        user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"
        headers = { "User-Agent" : user_agent }
        req = urllib2.Request(url, None, headers)
        try :
            urllib2.urlopen(req)
        except URLError, e:
            if hasattr(e, "reason") :
                print e.reason
                return None
            #sys.exit(1)

        try :
            response = urllib2.urlopen(req)
        except HTTPError, e:
            if hasattr(e, 'code'):
                print "The server couldn't fulfill the request."
                print 'Error code: ', e.code
                return None
            #sys.exit(1)

        url_data = response.read()
        #print "got html\n\n"
        if output_file == None:
            return url_data
        else:
            try:
                #f = open("%s/output_file", "wb") % ("/home/webadmin/scrollmotion.virtual.vps-host.net/html/xml/chicagotribunesportsreader/images")
                #self.image_repository = "/home/webadmin/scrollmotion.virtual.vps-host.net/html/xml/chicagotribunesportsreader/images/"
                #filename = self.image_repository+ output_file
                ## asset something here
                filename = output_file
                f = open(filename, "wb")
                f.write(url_data)
                f.close()
            except IOError, e:
                #raise IOError, e
                print >>sys.stderr, "Could not open %s for writing! %s" % (output_file, e)


    def image_gallery_generator (self, link, max) :
        #max = max+1  # range returns [min, max)
        for i in range(1,max+1):
            found_img_class = 0
            a_link = link + "?index=%s" % i
            print "DEBUG link : a_link %s" % a_link
            html = self.do_fetch(a_link)
            soup = BeautifulSoup(html)
            for image in soup.findAll("img", { "class" : "gallery-slideshow-photo" }):
                #print "Ga Ga!"
                found_img_class = 1
                yield image.attrs
            if not found_img_class:
                for image in soup.findAll('img', src = re.compile(r'\d{4}-\d{2}\/\d{6,}\.jpg')):
                    yield image.attrs

        return
        

    def scrape_story_generator (self, html, base_url) :
        photo_links = []
        href_re = re.compile(r'href="(.*\.photogallery)"')
        #photogallery = re.compile(r'.*href=\"(\/.*\.photogallery)\".*')
        soup = BeautifulSoup(html)
        ## Ah!  This is not always true!!!
        for d in soup.findAll(id="module-related-links"):
         #for d in soup.findAll('div'):
            for link in d.findAll ('a'):
                #print link
                #print str(link)
                m = href_re.search(str(link))
                if m:
                    print "Cool!"
                    print m.group(1)
                    print base_url + m.group(1)

                    #yield "http://www.chicagotribune.com" + m.group(1)
                    #photo_links.append("http://www.chicagotribune.com" + m.group(1))
                    photo_links.append(base_url + m.group(1))
        #        else:
        #            print "No matches in a div, try an image match?"
        #            break
        #if not photo_links:
            ## try an image match
        #    print "Got here"
        #    soup = BeautifulSoup(html)
        #    for img in soup.findAll ('img', src = re.compile(r'\d{4}-\d{2}\/\d{6,}\.jpg')):
                #photo_links.append(base_url + str(img.src).encode('ascii')
        #        print "Found images ... get src"
        #        src_re = re.compile(r'src="([^"]+)"')
        #        m = src_re.search(str(img).encode('ascii'))
        #        if m:
        #            print base_url + m.group(1)
        #            photo_links.append(base_url + m.group(1))
        return photo_links


    def how_many_images (self, html_of_photogallery) :
        soup = BeautifulSoup(html_of_photogallery)
        range_re = re.compile(r'(?:Image)*\s\d+ of (\d+)')
        for d in soup.findAll('div', { 'id' : 'photo-index' } ):
            range_string = d.contents[0].strip()
            m = range_re.match(range_string)
            if m:
                print "W000t!"
                print m.group(1)

                return int(m.group(1))
            else:
                return 0
    
    def really_how_many_images ( self, html_of_photogallery ) :
        """ now we are looking all over for the number of images in this
            gallery ... ARGH!!!!!!
        """
        # pdb.set_trace()
        soup = BeautifulSoup(html_of_photogallery)
        range_re = re.compile(r'1 of (\d+)')
        ## try looking in a span tag ...
        ## this seems to be one of the two templates ChicagoSports uses
        for span in soup.findAll('span', { 'class' : 'text' }):
            print "Try this ... %s" % span.contents[0].strip()
            range_string = span.contents[0].strip()
            m = range_re.match(range_string)
            if m:
                print "Found a value for max number of photos in gallery"
                print m.group(1)
                return int(m.group(1))
            else:
                return 0

    # FIXME
    # self.render_template (self.item_id, self.item_url, self.item_titleline, self.item_date, all_images)
    def render_template (self, id, url, title, date, all_images) :
        entries = []
        image_link = ""
        print "DEBUG: id : %s, aggregator : %r " % (id, all_images)
        #rss_template = XMLTemplate(id, date)
        channel_template = XMLTemplate.RssChannel(title, url, self.item_titleline)
        item_template =  XMLTemplate.RssItem(id, url, "TITLE")
        for img_attrs in all_images:
            print img_attrs['src']
            print img_attrs['alt']
            image_url = img_attrs['src']
            parts = image_url.split('/')
            image_link = './' + parts[-2] + '/' + parts[-1]
                #print i['height']
                #print i['width']
            rss_image = XMLTemplate.RssImage(img_attrs['src'], image_link, img_attrs['alt'], img_attrs['alt'], 0, 0 )
            entries.append(rss_image)

        template_file = "failover/images.tmpl"
        template = Template(
            file = template_file,
            searchList = [
                { "channel_title" : channel_template.title,
                    "channel_link" : channel_template.desc,
                    "channel_desc" : channel_template.desc,
                    "item_guid" : item_template.guid,
                    "item_link" : item_template.link,
                    "item_title" : item_template.title,
                    "item_images" : entries
            } ] 
        )

        print str(template)
        try:
            xml_out_filename = self.xml_path + id + ".images.xml"
            xml_file = open(xml_out_filename, "w")
            xml_file.write(str(template))
            xml_file.close()
        except IOError, e:
           #raise IOError, e
           print >>sys.stderr, "Could not open %s for writing! %s" % (output_file, e)



        #xml_template = XMLTemplate (id, date, title, url, images) 


class XMLTemplate(object) :
    def __init__(self, rss_id, rss_date):
        self.rss_id = rss_id
        self.rss_date = rss_date
        #self.rss_titles = rss_titles
        #self.rss_urls = rss_urls
        #self.rss_images = rss_images

    class RssChannel (object) :
        def __init__ (self, title, link, desc = ""):
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
        def __init__(self, url, link, title, desc, height = 0, width = 0):
            self.url = url
            self.link = link
            self.title = title
            self.desc = desc
            self.height = height
            self.width = width

    class RssEntry (object):
        def __init__(self, rss_channel, rss_item, rss_image):
            self.rss_channel = rss_channel
            self.rss_item = rss_item
            self.rss_image = rss_image

    def write_template(self, rss_channel, rss_item, rss_entries, rss_images):
        entries = []
        for entry in rss_entries:
            entries.append(RssEntry(rss_channel, rss_item, entry))

        template_file = "failover/images.tmpl"
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

        #print str(template)
        #xml_out_filename = self.xml_path + 
        #xml_file = open(


if __name__ == '__main__':

    ## test examples as of 7/23/2008
    item = { 'item_id' : '41037713',
            'item_titleline' : 'Tribune reporter',
            'item_url' : 'http://chicagosports.chicagotribune.com/sports/cs-080715-world-series-poker-tim-loecke,1,959230.story',
            'item_date' : '2008-07-15'
    }


    pg = PhotoGallery(item['item_id'], item['item_url'], item['item_titleline'], item['item_date'])
    pg.get_photogallery_urls()

    item = { 'item_id' : '41008173', 'item_titleline' : 'AP National Writer',
            'item_url' : 'http://www.chicagotribune.com/sports/sns-ap-glf-british-open,0,285322.story',
            'item_date' : '2008-07-20' 
    }

    pg = PhotoGallery(item['item_id'], item['item_url'], item['item_titleline'], item['item_date'])
    pg.get_photogallery_urls()


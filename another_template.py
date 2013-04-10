#!  /usr/bin/python

from Cheetah.Template import Template

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
        self.link = url
        self.height = height
        self.width = width
    
class RssEntry (object):
    def __init__(self, rss_channel, rss_item, rss_image):
        self.rss_channel = rss_channel
        self.rss_item = rss_item
        self.rss_image = rss_image

def write_template ():
    entries = []
    rss_channel = RssChannel( 
        "this is a title", 
        "this is a link", 
        "this is a desc")
    rss_item = RssItem( 
        41038532, 
        "http://www.chicagotribune.com/sports/cs-080715-morrissey-yankee-stadium-all-star-game,0,6821898.column", 
        "In the wake of the news",
        [
            "images/2008-07-16-41038543.jpg", 
            "images/2008-07-16-41038608.jpg",
            "images/2008-07-16-41038611.jpg",
            "images/2008-07-16-41038645.jpg"
        ])
    rss_image_a = RssImage ("http://scrollmotion.virtual.vps-host.net/xml/chicagotribunesportsreader/images/2008-07-16-41038543.jpg", 
        "&amp;#133;and Minnesota's Justin Morneau slides under the tag of Braves catcher Brian McCann with the winning run.", 
        "an image of Foo and Bar"
        )
    rss_image_b = RssImage ("http://scrollmotion.virtual.vps-host.net/xml/chicagotribunesportsreader/images/2008-07-16-41038608.jpg", 
        "Twins' Justin Morneau celebrates with White Sox's Carlos Quentin after Morneau scored the winning run on a sacrifice fly by Texas' Michael Young in the 15th inning.", 
        "an image of Foo not Bar")

    rss_image_c = RssImage ("http://scrollmotion.virtual.vps-host.net/xml/chicagotribunesportsreader/images/2008-07-16-41038611.jpg", 
        "Michael Young hits a fly ball in the 15th inning&amp;#133;", 
        "an image of Foo not Bar")

    rss_image_d = RssImage ("http://scrollmotion.virtual.vps-host.net/xml/chicagotribunesportsreader/images/2008-07-16-41038645.jpg", 
        "Michael Young hits a fly ball in the 15th inning&amp;#133;", 
        "an image of Foo not Bar")

    entries.append(RssEntry(rss_channel,rss_item,rss_image_a))
    entries.append(RssEntry(rss_channel,rss_item,rss_image_b))
    entries.append(RssEntry(rss_channel,rss_item,rss_image_c))
    
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
              "item_images" : [rss_image_a, rss_image_b, rss_image_c, rss_image_d]
            } ] 
    )

    print str(template)

if __name__ == '__main__' :
    write_template()

    


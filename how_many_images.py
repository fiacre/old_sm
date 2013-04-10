#!  /usr/bin/python

import urllib2
from urllib2 import URLError, HTTPError
import socket
from BeautifulSoup import BeautifulSoup
import sys
import re


def do_fetch(url) :
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

    html = response.read()
    return html

def how_many_images ( html ) :
    soup = BeautifulSoup(html)
    range_re = re.compile(r'Image \d+ of (\d+)')
    for d in soup.findAll('div', { 'id' : 'photo-index' } ):
        range_string = d.contents[0].strip()
        m = range_re.match(range_string)
        if m:
            return m.group(1)
            

if __name__ == '__main__':
    url = sys.argv[1]
    if url != None:
        html = do_fetch(url)
        max = how_many_images (html)
        if max:
            print max
        else:
            print >>sys.stderr, "Didn't get a value from regex"
    else:
        print >>sys.stderr, "Usage : %s <url>" % sys.argv[0]


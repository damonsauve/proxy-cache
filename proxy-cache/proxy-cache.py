#!/usr/bin/python

"""..."""

from BaseHTTPServer import BaseHTTPRequestHandler
import urllib2
import hashlib
import redis

HOST = '127.0.0.1'
PORT = 8080

class Handler(BaseHTTPRequestHandler):

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    cache_key = ''

    def do_GET(self):
        """..."""

        if len(self.path) > 0:
            page = self.get_page()

        if page:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(page)
        else:
            """..."""

        return

    def get_page(self):
        """..."""

        #self.set_redis()
        self.set_cache_key();

        page = self.fetch_page_from_cache()

        if page:
            print 'cached'
        else:
            print 'not cached'
            page = self.fetch_page_from_url()
            self.cache_page(page)

        return page

    def set_cache_key(self):
        m = hashlib.md5()
        m.update(self.path)
        self.cache_key = m.digest()
        print "cache_key is {}".format(self.cache_key)
        return

    def fetch_page_from_cache(self):
        """..."""
        page = self.r.get(self.cache_key)

        return page

    def fetch_page_from_url(self):
        """..."""
        request = urllib2.Request(self.path)
        request.add_header('User-agent', self.headers['user-agent'])
        response = urllib2.urlopen(request)
        page = response.read()
        return page

    def cache_page(self, page):
        """..."""
        self.r.set(self.cache_key, page)
        return

def main():
    """..."""
    server_address = (HOST, PORT)
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(server_address, Handler)
    server.serve_forever()

if __name__ == '__main__':
    main()

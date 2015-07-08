#!/usr/bin/python

"""..."""

from BaseHTTPServer import BaseHTTPRequestHandler
import urllib2
#import urlparse
import redis

HOST = '127.0.0.1'
PORT = 8080

class Handler(BaseHTTPRequestHandler):

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

        is_cached = self.check_cache()

        if is_cached:
            print 'cached'
            page = self.fetch_page_from_cache()
        else:
            print 'not cached'
            page = self.fetch_page_from_url()
            self.cache_page(page)

        return page

    def check_cache(self):
        """..."""
        return False

    def fetch_page_from_cache(self):
        """..."""
        return True

    def fetch_page_from_url(self):
        """..."""
        request = urllib2.Request(self.path)
        request.add_header('User-agent', self.headers['user-agent'])
        response = urllib2.urlopen(request)
        page = response.read()
        return page

    def cache_page(self, page):
        """..."""
        return True

def main():
    """..."""
    server_address = (HOST, PORT)
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(server_address, Handler)
    server.serve_forever()

if __name__ == '__main__':
    main()

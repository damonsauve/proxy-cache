"A simple proxy cache for web browsers using Python's HTTP server and Redis."

import sys
import urllib2

from BaseHTTPServer import BaseHTTPRequestHandler

class Proxy(BaseHTTPRequestHandler):

    def __init__(self, cache, *args):
        self.cache = cache
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        "Handle HTTP GET requests."

        if len(self.path) > 0:
            page = self.get_page()

        if page:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(page)
        else:
            self.send_error(404)

        return

    def get_page(self):
        """
        Get cached page if available, otherwise fetch the URL,
        and then cache it.
        """

        page = self.cache.fetch_page_from_cache(self.path)

        if page:
            print 'cached'
        else:
            print 'not cached'
            page = self.fetch_page_from_url()
            self.cache.cache_page(page)

        return page

    def fetch_page_from_url(self):
        "Get page from live URL; pass user-agent from the client request."

        request = urllib2.Request(self.path)
        request.add_header('User-agent', self.headers['user-agent'])
        response = urllib2.urlopen(request)

        return response.read()

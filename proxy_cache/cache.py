"""Simple page caching with Redis as the data store."""

import os
import json
import hashlib
import redis

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONF_FILE = os.path.join(ROOT_DIR, 'conf/cache.json')

class Cache:

    # Redis key to cached page.
    #
    cache_key = False

    # Redis name spaces.
    #
    cache_key_prefix = 'cache-key-'
    cache_list       = 'cached-pages'

    def __init__(self, host, port):
        """Initialize Redis connection."""

        self.redis_host = host
        self.redis_port = port

        self.load_configs()

        self.connect()

    def load_configs(self):
        """Load JSON config file."""
        self.config = json.load(open(CONF_FILE))

    def connect(self):
        """Connect to Redis instance."""

        self.r = redis.StrictRedis(
                host=self.redis_host,
                port=self.redis_port,
                db=0
            )

    def fetch_page_from_cache(self, path):
        """Get cached page."""

        self.set_cache_key(path);

        return self.r.get(self.cache_key)

    def cache_page(self, page):
        """Cache the page."""

        self.manage_cache()

        # Set key and string value.
        #
        self.r.set(self.cache_key, page)

        # set redis key expiration (TTL in seconds).
        #
        #self.r.expire(self.cache_key, self.config['cacheDuration'])

        # Add page to list.
        #
        self.r.lpush( self.cache_list, self.cache_key)
        print "pushing {}".format(self.cache_key)

        return

    def set_cache_key(self, path):
        """Create cache key name."""

        m = hashlib.md5(path.encode())
        self.cache_key = self.cache_key_prefix + m.hexdigest()

        #print "cache_key is {}".format(self.cache_key)

        return

    def manage_cache(self):
        """Manage the cache prior to adding to it."""
        check_cache_expires()
        check_cache_count()
        check_cache_size()
        return

    def check_cache_expires(self):
        """..."""
        pass

    def check_cache_count(self):
        """Delete pages from cache if the max number of cached pages is reached."""

        # First, check number of elements in cache and delete oldest one if total = max size.
        #
        cache_count = self.get_cache_count()

        #print "cache_count: {}/{}".format(cache_count, self.config['cacheSizeElements'])

        if cache_count == self.config['cacheSizeElements']:
            removed = self.r.rpop(self.cache_list)
            #print "removed {}".format(removed)

        #new_cache_count = self.get_cache_count()
        #print "new cache_count: {}/{}".format(cache_count, self.config['cacheSizeElements'])

        return

    def get_cache_count(self):
        """Redis call to number of elements in list."""
        return self.r.llen(self.cache_list)

    def check_cache_size(self):
        """..."""
        pass

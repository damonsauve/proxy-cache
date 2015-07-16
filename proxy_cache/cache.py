"Simple page caching with Redis as the data store."

import calendar
import hashlib
import json
import os
import redis
import sys
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONF_FILE = os.path.join(ROOT_DIR, 'conf/cache.json')


class Cache(object):

    # Redis hash containing cached page and page size. key name is combo of prefix
    # and md5(url).
    #
    cache_key = None

    # prefix for cached-page keys.
    #
    cache_key_prefix = 'cache-key-'

    # field names for Redis cached-page hash.
    #
    FIELD_PAGE = 'page'
    FIELD_SIZE = 'size'

    # ordered list of cache key, with UTC as score.
    #
    cache_max_utc = 'cache-max-utc'

    # Redis list of cached pages used to keep track of oldest cached item.
    #
    cache_max_count = 'cache-max-count'

    # Redis string with current size of cache in bytes.
    #
    cache_bytes = 'cache-bytes'

    def __init__(self, host, port):
        "Initialize Redis connection."

        self.redis_host = host
        self.redis_port = port
        self.load_configs()
        self.connect()

    def load_configs(self):
        "Load JSON config file."
        self.config = json.load(open(CONF_FILE))

    def connect(self):
        "Connect to Redis instance."
        self.r = redis.StrictRedis(
                host=self.redis_host,
                port=self.redis_port,
                db=0
            )

    def manage_cache(self):
        "Manage the cache prior to adding to it."
        self.check_cache_expires()
        self.check_cache_count()
        #self.check_cache_bytes()

    def check_cache_expires(self):
        "Call Redis to fetch and delete members from a list of keys that have expired UTC timestamps."

        utc = self.get_utc_now()
        utc_expired = utc - self.config['cacheDuration']
        keys = self.r.zrangebyscore(self.cache_max_utc, 0, utc_expired)

        if len(keys) > 0:
            for key in keys:
                self.remove_key_from_utc_index(key)
                self.remove_page_from_cache(key)
                print "** expired page {}".format(key)

    def get_utc_now(self):
        "Return current UTC."
        return calendar.timegm(time.gmtime())

    def remove_key_from_utc_index(self, key):
        "Call Redis to delete key from UTC index."
        self.r.zrem(self.cache_max_utc, key)

    def remove_page_from_cache(self, key):
        "Call Redis to delete key from page cache."
        self.r.delete(key)

    def check_cache_count(self):
        "Delete oldest page from cache if the max number of cached pages is reached."

        # get total number of items in list.
        #
        cache_count = self.get_cache_count()

        print "** current cached page count {}".format(cache_count)

        # if total items equals max cache elements, remove oldest item.
        #
        if cache_count >= self.config['cacheSizeElements']:
            removed = self.r.rpop(self.cache_max_count)
            self.remove_page_from_cache(removed)
            print "** deleted page {}".format(removed)

    def get_cache_count(self):
        "Call Redis to fetch number of elements in list."
        return self.r.llen(self.cache_max_count)

    def check_cache_bytes(self):
        """
        If total cache size exceeds the configured value, delete the oldest
        item until within configuration.
        """

        print "*** current cache size {}".format(self.get_cache_bytes())

        while ( int(self.get_cache_bytes()) - int(self.config['cacheSizeBytes']) ) > 0:

            # pop last item off counter list
            #
            popped_key = self.r.rpop(self.cache_max_count)

            # get size of this page
            #
            bytes_removed = self.r.hget(popped_key, self.FIELD_SIZE )
            print "*** bytes_removed {}".format(bytes_removed)

            cache_bytes = int(self.get_cache_bytes())
            new_size =  int(cache_bytes) - int(bytes_removed)
            print "*** new size = {} - {} = {}".format(cache_bytes, bytes_removed, new_size)
            self.r.set(self.cache_bytes, new_size)

            # drop key from other lists too
            #
            self.remove_key_from_utc_index(popped_key)
            self.remove_page_from_cache(popped_key)

    def get_cache_bytes(self):
        "Call Redis to fetch current cache size."
        bytes = self.r.get(self.cache_bytes)
        if bytes == None:
            return 0
        else:
            return bytes

    def fetch_page_from_cache(self, path):
        "Get cached page."
        self.set_cache_key(path);
        return self.r.hget(self.cache_key, self.FIELD_PAGE)

    def set_cache_key(self, path):
        "Create cache key name."
        m = hashlib.md5(path.encode())
        self.cache_key = self.cache_key_prefix + m.hexdigest()

    def cache_page(self, page):
        "Cache the page."

        print "** cache key {}".format(self.cache_key)

        # add page to hash.
        #
        self.add_page_to_hash(page)

        # add page size to hash.
        #
        page_size = sys.getsizeof(page)
        self.add_size_to_hash(page_size)

        # add key to index of Unix timestamps (sorted set score = UTC).
        #
        self.add_utc_to_index()

        # add key to index of cached items.
        #
        self.add_page_to_count()

        # update total cache size.
        #
        cache_bytes = self.get_cache_bytes()
        new_size = int(page_size) + int(cache_bytes)
        self.r.set(self.cache_bytes, new_size)

    def add_page_to_hash(self, page):
        self.r.hset(self.cache_key, self.FIELD_PAGE, page)

    def add_size_to_hash(self, page_size):
        self.r.hset(self.cache_key, self.FIELD_SIZE, page_size )

    def add_utc_to_index(self):
        utc = self.get_utc_now()
        self.r.zadd(self.cache_max_utc, utc, self.cache_key)

    def add_page_to_count(self):
        self.r.lpush(self.cache_max_count, self.cache_key)

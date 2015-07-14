"Simple page caching with Redis as the data store."

import hashlib
import json
import os
import redis

import calendar
import time


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONF_FILE = os.path.join(ROOT_DIR, 'conf/cache.json')


class Cache(object):

    # Redis key to cached page.
    #
    cache_key = None

    # Redis name spaces.
    #
    cache_key_prefix = 'cache-key-'
    cache_list_count = 'cache-list-count'
    cache_list_utc = 'cache-list-utc'

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

    def fetch_page_from_cache(self, path):
        "Get cached page."

        self.set_cache_key(path);

        return self.r.get(self.cache_key)

    def cache_page(self, page):
        "Cache the page."

        # Set key and string value.
        #
        self.r.set(self.cache_key, page)

        print "** pushing {}".format(self.cache_key)

        utc = self.get_utc_now()

        # Add key to index of Unix timestamps.
        #
        self.r.zadd(self.cache_list_utc, utc, self.cache_key)

        # Add key to index of cached items.
        #
        self.r.lpush(self.cache_list_count, self.cache_key)

    def get_utc_now(self):
        "Return current UTC."
        return calendar.timegm(time.gmtime())

    def set_cache_key(self, path):
        "Create cache key name."
        m = hashlib.md5(path.encode())
        self.cache_key = self.cache_key_prefix + m.hexdigest()

    def manage_cache(self):
        "Manage the cache prior to adding to it."
        self.check_cache_expires()
        #self.check_cache_size()
        #self.check_cache_count()

    def check_cache_expires(self):
        "Call Redis to fetch and delete members from a list of keys that have expired UTC timestamps."

        utc = self.get_utc_now()
        utc_expired = utc - self.config['cacheDuration']
        keys = self.r.zrangebyscore(self.cache_list_utc, 0, utc_expired)

        if len(keys) > 0:
            for key in keys:
                self.r.zrem(self.cache_list_utc, key)
                self.remove_page_from_cache(key)

    def check_cache_size(self):
        "..."
        # maintain a key-value string in Redis that has total size in bytes and
        # delete pages from cache when necessary.
        pass

    def check_cache_count(self):
        "Delete oldest page from cache if the max number of cached pages is reached."

        # get total number of items in list.
        #
        cache_count = self.get_cache_count()

        # if total items equals max cache elements, remove oldest item.
        #
        if cache_count == self.config['cacheSizeElements']:
            removed = self.r.rpop(self.cache_list_count)
            self.remove_page_from_cache(removed)

    def get_cache_count(self):
        "Call redis to fetch number of elements in list."
        return self.r.llen(self.cache_list_count)

    def remove_key_from_utc_index(self, key):
        "Call Redis to delete key form UTC index."
        self.r.zrem(self.cache_list_utc, key)
        print "**** deleted UTC key: {}".format(key)

    def remove_page_from_cache(self, key):
        "Call Redis to delete key from page cache."
        self.r.delete(key)
        print "**** deleted cache key: {}".format(key)

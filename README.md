Mini Project & Code Sample

A simple proxy cache for web browsers using Python's HTTP server and Redis as the data store.

Quick start instructions:

Start up your local Redis on port 6379:

$ cd redis-3.0.1

$ src/redis-server

Clone and install this repo, then run the start-up command:

$ python setup.py install

$ python setup.py develop

$ cd proxy_cache/bin/

$ python ./run_proxy_cache

Open Firefox Preferences, and under Advanced -> Network, change your Connection settings to use:

Manual Proxy Configuration: localhost:8080

Now open any web page to start caching and serving cached pages.

Configuration Options

The proxy-cache configuration is set as JSON object in the file:

- proxy_cache/conf/cache.json

The default configs are:

{
    "cacheDuration": 30,
    "cacheSizeBytes": 10000,
    "cacheSizeElements": 9
}

cacheDuration, in seconds, determines how long a single page is stored in the cache.
cacheSizeBytes, in bytes, set the maximum size in bytes of all cached objects.
cacheSizeElements sets the maximum number of cached objects.

For each setting, when the maximum value is reached, the oldest item in the cache is purged.

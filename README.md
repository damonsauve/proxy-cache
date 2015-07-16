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

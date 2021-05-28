from gevent.monkey import patch_all; patch_all()

from pywb.apps.frontendapp import FrontEndApp
from warcio.timeutils import http_date_to_datetime, timestamp_now

from tempfile import SpooledTemporaryFile

import os
import redis
import logging
import traceback
import re

# ============================================================================
class RBSProxyApp(FrontEndApp):
    def __init__(self, config_file=None, custom_config=None):
        super(RBSProxyApp, self).__init__(config_file='./config.yaml',
                                           custom_config=custom_config)

        self.redis = redis.StrictRedis.from_url(os.environ['REDIS_URL'], decode_responses=True)

    def proxy_route_request(self, url, environ):
        try:
            key = 'up:' + environ['REMOTE_ADDR']
            timestamp = self.redis.hget(key, 'timestamp') or timestamp_now()
            coll = self.redis.hget(key, 'coll')
            print(self.redis.hgetall(key))
            #environ['pywb_redis_key'] = key
            print('COLL', coll)
            environ['pywb_proxy_default_timestamp'] = timestamp
            return '/{0}/bn_/'.format(coll) + url
        except Exception as e:
            traceback.print_exc()
            return self.proxy_prefix + url


#=============================================================================
application = RBSProxyApp()

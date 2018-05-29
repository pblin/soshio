#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import json

import requests
import pymongo

import config.loader
import datetimes

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class WeiboStream:
    '''
          Parse and return posts from Socialgist Streamining API
    '''
    def __init__(self):
        self._get_post = self._get_feed()
        
    def _get_feed(self):
        url = config.loader.load().get('SOCIALGIST_SUBSCRIPTION_URL')
        logger.debug("Socialgist url: %s" % url)
        r = requests.get(url, stream=True)
        def get_post():
            for line in r.iter_lines():
                if line:
                    try:
                        yield json.loads(line)
                    except ValueError as e:
                        logger.error(line)
                        raise e
        return get_post

    def get_posts(self):
        for post in self._get_post():
            if (post['text']['type'] == 'comment' or post['text']['event'] != 'add'):
                logger.debug("Discard a comment for keyword <%s>" % post['match_info']['keyword'])
                continue #TODO: parse comments
            keyword = post['match_info']['keyword']
            status = post['text']['status']
            t = {
                    'id': status['mid'],
                    'datetime': datetimes.extract_datetime(status['created_at']),
                    'username': status['user']['name'],
                    'uid': status['user']['id'],
                    'text': status['text'],
                    'shares': status['reposts_count'],
                    'replies': status['comments_count'],
                    'uri': status['statusurl'].replace("http://",""),
                    'reach': status['user']['followers_count'],
                    'gender': status['user']['gender'],
                    'platform': 'sina weibo'
                }
            try:
                t['location'] = self._get_location(status['user']['city_name'], status['user']['province_name'], status['user']['city_coordinates'])
            except IndexError: # empty coordinates
                pass
            logger.debug("Got 1 post for keyword <%s>" % keyword)
            yield (keyword, t)

    def _get_location(self, city, province, coordinates):
        return {
                 'english': ", ".join([city, province]),
                 'raw': ", ".join([city, province]),
                 'coordinates': {
                                  'lng': float(coordinates.split(" ")[1]),
                                  'lat': float(coordinates.split(" ")[0])
                                }
                }


class KeywordManager:
    def __init__(self):
        self.base_url = config.loader.load().get('SOCIALGIST_KEYWORD_URL')
    
    def get_keywords(self):
        return set(requests.get(self.base_url).json())

    def add_keyword(self, keyword):
        payload = {"addAll":{"keyword":keyword}}
        r = requests.put(self.base_url, data=json.dumps(payload))
        if r.json()['result'] == 'success':
            return True
        print r.json()
        return False

    def delete_keyword(self, keyword):
        payload = {"keyword": keyword}
        r = requests.delete(self.base_url, params=payload)
        if r.json()['result'] == 'success':
            return True
        print r.json()
        return False

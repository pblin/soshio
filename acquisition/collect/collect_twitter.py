#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import twitter
import random

APP_CREDENTIALS = [ # TODO: migrate to OAuth2.0
        #name, app_key, app_secret, access_token, token_secret
        (u'Sentinalysis','RdLYjo1qj3UDwnoWl1wmA','rSDkBlmvQsAbt4Gv57p31ZC9Uvntmivc99ADgFaODI','439871945-SpUawnKeT0beUK9aEK1lsDSeq1r3jGSK746I4QDb','KcllcFY5Zo1c7DHlRkqZj7swEZxO3btYWW8g8OSPLY'),
        (u'SoshioAnalysis','HBtZnyceuGCJFfn0hYQu1g','ldFcVJQSmU4iDlQzOWvtXLEVbPg7RrrMFfUIpo2pb0','439871945-PcL3u8HMz9kHJjdTW1uWHGOo8p3drlfvsJq8KA4h','f9tpSncUnSBfVP46nLHPKXi3DWK3OcWiPSK11Hye1U'),
        (u'中文社群資料分析','P5GOCA6AlZA2mMTQGAoGEQ','ADScYBWf8Bz2MRoRphyVFqYUt4wtt16lI83uKjmkSME','439871945-lXiMlDgzasM9TmF8FAt0eboEEoUQtKoaZBQvdzd4','0vrYGDUB0gL8vpoeK0cpjViBGwPmXRqE27dW8NrjE'),
    ]

def get_client():
    _, app_key, app_secret, access_token, token_secret = random.choice(APP_CREDENTIALS)
    return twitter.Twitter(auth=twitter.OAuth(access_token,token_secret,app_key,app_secret))

def search(query, age_check=None):
    logging.debug('Requesting Twitter for query <{0}>'.format(repr(query)))
    max_id = ''
    for page in range(5):
        response = get_client().search.tweets(q=query,count=100,lang='zh',result_type='recent',max_id=max_id)
        for result in response['statuses']:
            if age_check and age_check(result.get('created_at')): raise StopIteration
            yield get_tweet(result)
        max_id = response.get('search_metadata',{}).get('max_id')
        if not max_id: break
        
def get_tweet(result):
    user = result.get('user') or {}
    return {
            'id':unicode(result['id']),
            'username':user.get('screen_name'),
            'gender':None,
            'location':user.get('location'),
            'text':result['text'],
            'datetime':result.get('created_at'),
            'shares':result.get('retweet_count'),
            'replies':None,
            'reach':user.get('followers_count'),
            'uri':u'twitter.com/{0}/status/{1}'.format(user.get('screen_name'), result['id'])
        }

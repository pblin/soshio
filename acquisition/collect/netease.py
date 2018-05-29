#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import json
import jianfan
import t4py.tblog
import t4py.oauth
import random

APP_CREDENTIALS = [
        #name, app_key, app_secret, access_token, token_secret
        (u'Thinkudo,談情','N2SxulMVk7QCOvHL','NJ0Ju3kp13Wvyl1CCoihj7htFR7lQJ9l','e04c9a810bf5f11cc820f58d27a9f679','f2c30f55919e570c8ee58c2e6ab30f91'),
        (u'Thinkudo,Sentianalysis','Mu2qIXqh6njuSPe1','GTxCnmyNFDaWJXWjQNJG40dI7pRn4NOp','ecc103f982b75b521e5bdc51e465f9ef','be4e35c5a979e91626d5a869502d22fc'),
        (u'Thinkudo,中文情感分析','TKuaxx6dGGgyJ1Mj','Ien4h8p0AewMrWcovsxrceS071PFC2uV','cd313a5462e4ec31722c6b594ac9e393','e3b98206e4a68a706a7b7b2b1b46f69d'),
        (u'Thinkudo,社交數據分析','Y7fhlAKQVfuvFxs1','bwpziEJjRQdvljotwd38KbIknu3lVzQD','c0fc31ac14acf89b061d5734def8eb6a','c22dd6e6875d4127416e70ea028ae6c8'),
        (u'Thinkudo,社交數據','KT5xCHL2bIhRCSjD','0QbFiXebddVN0tN10Q40ghFugxsRUokl','b60c8b12d44b6518c70ca1e637885133','b6193cbb6e9e0602c0d32536f7226b88'),
    ]

def search(query, age_check=None):
    query = jianfan.ftoj(query)
    logging.debug('Requesting 163 for query <{0}>'.format(repr(query)))
    
    params = {'q':query.encode('utf8'),'per_page':20}
    for page in range(25):
        params['page'] = page+1
        response = get_client().statuses_search(params)
        response = json.loads(response)
        if not response: break
        if type(response) is dict and response.get('error'):
            logging.warning(u'Netease has hit its access limit')
            break
        for result in response:
            if age_check and age_check(result.get('created_at')): raise StopIteration
            yield get_tweet(result)
           
def get_client():
    _, app_key, app_secret, access_token, token_secret = random.choice(APP_CREDENTIALS)
    client = t4py.tblog.TBlog(app_key, app_secret)
    client._request_handler.access_token = t4py.oauth.OAuthToken(access_token, token_secret)
    return client
    
GENDER = ['f','m',None]

def get_tweet(result):
    user = result.get('user', {})
    user_gender = GENDER[int(user.get('gender',2))]
    return {
            'id':unicode(result['id']),
            'username':user.get('screen_name'),
            'gender':user_gender,
            'location':user.get('location'),
            'text':result['text'],
            'datetime':result.get('created_at'),
            'shares':result.get('retweet_count'),
            'replies':result.get('comments_count'),
            'reach':user.get('followers_count'),
            'uri':u't.163.com/{0}/status/{1}'.format(user.get('name'),result['id'])
        }

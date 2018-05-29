#!/usr/bin/python
# -*- coding: utf-8 -*-

import jianfan
import logging
import plurk_oauth.PlurkAPI
import random

APP_CREDENTIALS = [ # TODO: migrate to OAuth2.0
        #name, app_key, app_secret, access_token, token_secret
        (u'Sentinalysis','61xIameXOmae','SZzh43A3zNnYKAVtdbRvcesaUm21Q09a','4ZkXz1U8Os22','Ps0hyKAbhVkFU3YcepVvkWwHgQNQOnuS'),
        (u'中文情感分析','g9OTqmWJ5A3M','YwIoYjjnFT6vjoIwfP7Sg7xftdHH0XE6','2L9xJw64GADG','PDAWMXthUhKFrZSRYbSv95BWz6iNX1vx'),
        (u'噗浪資料分析','McQERV3BgIQ4','WlktrlQy4f5WLV3o8e9gmdHb4R1Qczdn','A2xqzX87A5i3','CP96dpMnRFG9V0JNgpAbVIqnlmwGwGQr'),
    ]
    
def get_client():
    _, app_key, app_secret, access_token, token_secret = random.choice(APP_CREDENTIALS)
    plurk = plurk_oauth.PlurkAPI.PlurkAPI(app_key, app_secret)
    plurk.authorize(access_token, token_secret)
    return plurk

def search(original_query, age_check=None):
    query = jianfan.jtof(original_query)
    logging.debug('Requesting Plurk for query <{0}>'.format(repr(query)))
    offset = 0
    uri = u'/APP/PlurkSearch/search?query={0}'.format(query)
    for page in range(25):
        try:
            response = get_client().callAPI(u'{0}&offset={1}'.format(uri,offset or ''))
        except ValueError as error:
            logging.info(u'Received Plurk error <{0}> suggesting no results'.format(error.message))
            break
        if not response: break
        users = response.get('users') or {}
        for plurk in response.get('plurks',[]):
            if query.lower() not in plurk.get('content_raw').lower(): continue
            if age_check and age_check(plurk.get('posted')): raise StopIteration
            user_id = plurk.get('user_id')
            user = get_user_details(user_id) or users.get(user_id) or {}
            if user.get('default_lang') not in ('cn','tr_ch'): continue
            yield get_tweet(plurk, user)
        if not response.get('has_more'): break
        offset = response.get('last_offset')
        
def get_user_details(user_id):
    try:
        uri = u'/APP/Profile/getPublicProfile?user_id={0}'.format(user_id)
        user = get_client().callAPI(uri)
        user_info = user.get('user_info') or {}
        user_info['fans_count'] = user.get('fans_count')
        return user_info
    except Exception as error:
        logging.warning(u'Received Plurk error <{0}> during user detailing'.format(error.message))
    
GENDERS = ['f','m',None]

def get_tweet(plurk, user):
    return {
            'id':plurk['plurk_id'],
            'username':user.get('nick_name'),
            'gender':GENDERS[int(user.get('gender',2))],
            'location':user.get('location').replace(u', Taiwan',u' 台灣'),
            'text':plurk['content_raw'],
            'datetime':plurk.get('posted'),
            'shares':plurk.get('replurkers_count'),
            'replies':plurk.get('response_count'),
            'reach':user.get('fans_count'),
            'uri':u'plurk.com/'+user.get('nick_name')
        }

#!/usr/bin/python
# -*- coding: utf-8 -*-

import jianfan
import logging
import qqweibo
import random

APP_CREDENTIALS = [ # TODO: migrate to OAuth2.0
        #name, app_key, app_secret, access_token, token_secret
        (u'Soshio','801201050','bd947b244c27f8345f5038ca2fdda2bd','6c5e5a367b4148159623a2b251eb9928','3fe371bb3a4ba04089ae75a7e1dfc43f'),
        (u'Soshio談情 ','801254768','d3a3446c0466fd2b8a2da5241240a78f','ea45ddfd63bc45638ab202f81fec015e','31ab377661c657acc43590266af2f980'),
        (u'網路情感分析','801305369','dd9d66a0b7e2acf01f86d5d4be2ef670','a071b4d033d5450687e05941f8604b58','3adc77856a47495293567b04bd9a5452'),
        (u'社交數據分析','801308755','a95f206d86f08c639d09b0b31897df20','97fb806fa56649908b0128b522b1bfce','a17ce80218863b6f152f27797b971250'),
        (u'Soshio社交數據','801308757','a0249678b742d6561fdd309e6e1a4c4d','1e48bd513d1e4b7dbe491ed28d20dbdd','449e013ddad457f6feeb0eda6cb71868'),
        (u'社交數據','801364838','ca28135a5cf6824b05cf9afa25a37995','b7dfef030ecd4bdc8fed578e849ddfd7','edb14951701121201f530de7942a5151'),
        (u'Soshio數據','801364839','423761b3276b4ea697ab73bd2670eca9','03adf1c5cd1c440c907f724c4065054e','33f0f20a3cd402f14becd24302c288db'),
    ]

def get_client():
    _, app_key, app_secret, access_token, token_secret = random.choice(APP_CREDENTIALS)
    auth_handler = qqweibo.OAuthHandler(app_key, app_secret)
    auth_handler.setToken(access_token, token_secret)
    return qqweibo.API(auth_handler)
    
def search(query, age_check=None):
    query = jianfan.ftoj(query)
    logging.debug('Requesting Tencent for query <{0}>'.format(repr(query)))
    for page in range(17):
        try:
            results = get_client().search.tweet(query, 30, page+1)
        except qqweibo.error.QWeiboError as error:
            logging.warning(u'Received Tencent error <{0}>'.format(error.message))
            if u'rate' in error.message: break
            continue
        usernames = [tweet.name for tweet in results]
        users = dict((user.name, user) for user in get_client()._user_infos(usernames))
        for tweet in results:
            if age_check and age_check(tweet.timestamp): raise StopIteration
            if query not in tweet.text: continue
            yield get_tweet(tweet, users)
    
GENDERS = [None,'m','f']
get_gender = lambda i : GENDERS[i] if i < len(GENDERS) else None
    
def get_tweet(tweet, users):
    user = users[tweet.name]
    id = unicode(tweet.id)
    return {
            'id':id,
            'username':user.nick or user.name,
            'gender':get_gender(user.sex),
            'location':tweet.location,
            'text':tweet.text,
            'datetime':tweet.timestamp,
            'shares':tweet.count,
            'replies':tweet.mcount,
            'reach':user.idolnum,
            'uri':u't.qq.com/p/t/'+id
        }

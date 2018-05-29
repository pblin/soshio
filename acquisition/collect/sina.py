#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import random
import collections
import jianfan
import requests
import re
import json

APP_CREDENTIALS = {
        (u'us@getsoshio.com',u'13ass@ssins'):[
            ('2037343500','c0b3eae41b81ed275b26b23f41bf01f8'),
            ('1223011909','55147646f4bb49d78213ffbcc0011bf9'),
            ('1002922569','fac9ba6d9187d95b8074662b944c8cb5'),
        ],
        
        (u'whosbacon@gmail.com',u'analyzeTheWeb'):[
            ('409980230','054ab84419d1cceff3d866874a7c1249'),
            ('1938791691','4c0c14ff118c395fd26339cf7ded0742'),
            ('1238521281','c4b9b5b63cb67197636d2a553a87bab6'),
        ],
        
        (u'team@thinkudo.com',u'analyzeTheWeb'):[
            ('722506321','919a2c0b0f604c2330a8e94034cbd141'),
            ('746277687','10c8e66abb7b499e4e52df0eab7cb0c1'),
            ('2299258682','9b83978c90d294951dcaf4905e4fb2b7'),
        ],
    }
    
def get_credential():
    credential = random.choice(APP_CREDENTIALS.keys())
    return credential, random.choice(APP_CREDENTIALS[credential])
    
def get_appkey():
    credential, app_credential = get_credential()
    return credential, app_credential[0]
    
def search(query, age_check=None):
    query = jianfan.ftoj(query)
    logging.debug('Requesting Sina for query <{0}>'.format(repr(query)))
    for page in range(25):
        uri = u'http://s.weibo.com/weibo/{0}?page={1}'.format(query, page+1)
        response = requests.get(uri)
        next_page = False
        user_posts = collections.defaultdict(list)
        for post_info in scrape_posts(response.text):
            if age_check and age_check(post_info.get('datetime')): continue
            next_page = True # if at least one post one page passes age_check, try next page
            user_posts[post_info.pop('uid')].append(post_info)
        user_infos = get_user_infos(user_posts.keys())
        for uid, post_infos in user_posts.items():
            for post_info in post_infos:
                post_info.update(user_infos.get(uid) or {})
                yield post_info
        if not next_page: break
        
forward_finder = re.compile(ur'<dl class=\\"comment(.+?)<\\/dl>',flags=(re.UNICODE))
id_finder = re.compile(r'dl class=\\"feed_list\\" mid=\\"(\d+)\\"')
date_finder = re.compile(r'date=\\"(\d+)\\" class=\\"date\\"')
user_finder = re.compile(ur'nick-name=\\"(.+?)\\"',flags=(re.UNICODE))
content_finder = re.compile(ur'<em>(.+?)<\\/em>',flags=(re.UNICODE))
repost_finder = re.compile(ur'\\u8f6c\\u53d1(\(\d+\))?')
comment_finder = re.compile(ur'\\u8bc4\\u8bba(\(\d+\))?')
post_finder = re.compile(ur'a href=\\"http:\\/\\/(weibo.com\\/\d+\\/\w+\\)" title')
uid_finder = re.compile(ur'a href=\\"http:\\/\\/weibo.com\\/(\d+)\\/\w+\\" title')
def scrape_posts(text): # TODO: test!
    text = forward_finder.sub(u'',text)
    ids = id_finder.findall(text)
    dates = date_finder.findall(text)
    users = user_finder.findall(text)
    contents = content_finder.findall(text)
    reposts = repost_finder.findall(text)
    comments = comment_finder.findall(text)
    post_uris = post_finder.findall(text)
    uids = uid_finder.findall(text)
    for i, id in enumerate(ids):
        yield {
                'id': id,
                'datetime': int(dates[i]) / 1000,
                'username': json_to_unicode(users[i]),
                'uid': uids[i],
                'text': json_to_unicode(clean_scraped_content(contents[i])),
                'shares': clean_scraped_stat(reposts[i]),
                'replies': clean_scraped_stat(comments[i]),
                'uri': post_uris[i].replace('\\','')
            }

alt_finder = re.compile(ur'alt=\\"(.+?)\\"',flags=(re.UNICODE))
img_finder = re.compile(ur'<img[^<]*?>',flags=(re.UNICODE))
tag_finder = re.compile(ur'<[^<]*?>',flags=(re.UNICODE))
def clean_scraped_content(content): # TODO: test!
    alts = alt_finder.findall(content)
    imgs = img_finder.findall(content)
    for i, img in enumerate(imgs):
        if i >= len(alts): break
        content = content.replace(img, alts[i])
    return tag_finder.sub(u'',content).strip()
    
digit_finder = re.compile(r'\d+')
def clean_scraped_stat(stat):
    digits = digit_finder.findall(stat)
    if digits: return int(digits[0])
    
def json_to_unicode(text):
    return json.loads(u'"{0}"'.format(text))
    
def get_user_infos(uids):
    if not uids: return {}
    sampled_uids = random.sample(uids, len(uids)/10+1)
    nonsampled_uids = set(uids).difference(sampled_uids)
    user_infos = dict(get_follower_count(nonsampled_uids))
    user_infos.update(filter(None, map(get_user_detail, sampled_uids)))
    return user_infos
    
def get_follower_count(uids):
    if not uids: raise StopIteration
    credential, appkey = get_appkey()
    uri = u'https://api.weibo.com/2/users/counts.json?uids={0}&source={1}'.format(','.join(uids), appkey)
    response = requests.get(uri, auth=credential).json()
    check_error(response)
    for result in response or []:
        yield result['id'], {'reach':result['followers_count']}
    
def get_user_detail(uid):
    credential, appkey = get_appkey()
    uri = u'https://api.weibo.com/2/users/show.json?uid={0}&source={1}'.format(uid, appkey)
    response = requests.get(uri, auth=credential).json()
    try:
        check_error(response)
    except StopIteration:
        return
    return uid, {
        'gender':response.get('gender'),
        'location':response.get('location'), 
        'reach':response.get('followers_count')
    }
    
def check_error(response):
    if not response:
        raise StopIteration
    if 'error' in response and response['error']:
        logging.warning('Received Sina error <{0}>'.format(response.get('error')))
        raise StopIteration

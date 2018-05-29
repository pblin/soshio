#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import formator
import itertools
import jianfan

import collect_twitter as twitter
import plurk
import sina
import tencent
import netease

search_funcs = {
        'twitter': twitter.search,
        'plurk': plurk.search,
        'netease weibo': netease.search,
    }

def search(query_obj, *args, **options):
    logging.info(u'Collecting data for query <{0}> via keywords <{1}>'.format(query_obj.query, query_obj.keywords))
    search_keyword = get_search_keyword(query_obj, **options)
    return list(result for keyword in query_obj.keywords for platform_results in search_keyword(keyword) for result in platform_results)
    
def get_search_keyword(query_obj, **options):
    limited_search_funcs = list(get_search_funcs(query_obj, **options))
    def search_keyword(keyword):
        keyword = keyword.replace(u'\uff0e','.')
        for platform, limited_search_func in limited_search_funcs:
            logging.debug(u'Collecting data for keyword <{0}> on platform <{1}>'.format(keyword, platform))
            try:
                results = list(limited_search_func(keyword))
                yield formator.map_results(query_obj.query, platform, results)
            except Exception as error:
                logging.error(u'Failed data collection for <{0}> on <{1}> with <{2}>'.format(keyword, platform, error))
    return search_keyword
    
def get_search_funcs(query_obj, platforms=None, **options):
    matches_query = get_matches_query(query_obj)
    for platform in platforms or search_funcs.keys():
        if platform not in search_funcs: continue
        yield platform, get_limited_search_func(search_funcs[platform], matches_query, **options)
    
def get_matches_query(query_obj):
    standardize = lambda text : jianfan.ftoj(text.lower())
    def matches_query(post):
        inputs = [standardize(arg) in standardize(post['text']) for arg in query_obj.args]
        return query_obj.match(*inputs)
    return matches_query
    
def get_limited_search_func(search_func, matches_query, is_old=None, limit=100):
    def limited_search_func(keyword):
        search_results = search_func(keyword, is_old)
        filtered_results = itertools.ifilter(matches_query, search_results)
        for i, result in enumerate(filtered_results):
            if i < limit:
                yield result
                continue
            break
    return limited_search_func
    

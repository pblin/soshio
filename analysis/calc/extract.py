#!/usr/bin/python
# -*- coding: utf-8 -*-

import itertools
import re

### Utility class for specialized term extract
    
def filter_ignore(iter_terms, ignore):
    should_remove = lambda term: term in ignore or term.upper() in ignore or term.lower() in ignore or term.title() in ignore
    return itertools.ifilterfalse(should_remove, iter_terms)

def filter_exist(iter_terms, text):
    should_keep = lambda term: term in text or term.upper() in text or term.lower() in text or term.title() in text
    return itertools.ifilter(should_keep, iter_terms)

partofer = re.compile(ur'(\w{1,2})的(\w{1,2})',flags=(re.UNICODE))
def yield_terms_around_partof(text):
    for terms in partofer.findall(text):
        for term in terms:
            yield term
    
brackets = (u'［］',u'【】',u'《》',u'##',u'＜＞',u'「」',u'『』')
bracketers = dict((bracket, re.compile(ur'\{0}([^\{1}\r\n]*)\{1}'.format(*bracket),flags=(re.UNICODE))) for bracket in brackets)
def yield_bracketed_terms(text, bracket=None):
    for bracketer in bracketers.values() if bracket not in brackets else [bracketers.get(bracket)]:
        for term in bracketer.findall(text):
            yield term
        
titles = (u'先生',u'小姐',u'女士')
titlers = tuple(re.compile(ur'(\w{1,3})' + title,flags=(re.UNICODE)) for title in titles)
def yield_names_near_titles(text):
    for titler in titlers:
        for term in titler.findall(text):
            yield term

usernamer = re.compile(ur'\@(\w+)\W?',flags=(re.UNICODE))
def yield_usernames(text):
    return usernamer.findall(text)

quoters = (
        re.compile(ur'\/{2}\@\w+\W([^\/]+)',flags=(re.UNICODE)),
        re.compile(ur'\|{2}\@\w+\W([^\|\@]+)',flags=(re.UNICODE))
    )
def yield_quotes(text):
    for quoter in quoters:
        for quote in quoter.findall(text):
            yield quote.strip()
            
urier = re.compile(r'http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}[^\s]*')
def yield_uris(text):
    return urier.findall(text)
    
symboler = re.compile(ur'\W',flags=(re.UNICODE))
def clean_symbols(text):
    return symboler.sub(u' ',text)
    
import unittest

class ExtractTests(unittest.TestCase):
    def test_yield_terms_around_partof(self):
        result = list(yield_terms_around_partof(u'今天的天氣不錯'))
        self.assertNotIn(u'的',result)
        for term in (u'今天',u'天氣'):
            self.assertIn(term,result)
        
    def test_yield_bracketed_terms(self):
        result = list(yield_bracketed_terms(u'【值得看很多遍的勵志電影推存】《壞孩子的天空》、［自閉歷程］、#我的名字叫可汗#、＜黑天鹅＞ #http://t.cn/zOEY4sN '))
        for term in (u'值得看很多遍的勵志電影推存',u'壞孩子的天空',u'自閉歷程',u'我的名字叫可汗',u'黑天鹅'):
            self.assertIn(term, result)
        result2 = list(yield_bracketed_terms(u'【视频：AKB48史上最全200首歌曲串烧！】 http://t.cn/zOy5E2a （分享自 @优酷网）'))
        self.assertIn(u'视频：AKB48史上最全200首歌曲串烧！', result2)
        result3 = list(yield_bracketed_terms(u'《壞孩子的天空》 http://t.cn/zOy5E2a （分享自 @优酷网）', bracket=u'《》'))
        self.assertIn(u'壞孩子的天空', result3)
            
    def test_yield_names_near_titles(self):
        result = list(yield_names_near_titles(u'陳先生說得不錯 莊家玲小姐一點都不高'))
        for term in (u'陳',u'莊家玲'):
            self.assertIn(term, result)
            
    def test_yield_usernames(self):
        result = list(yield_usernames(u'好帅的五月天。我一直很喜欢的洒脱。//@冷笑话精选:都听过么？'))
        self.assertIn(u'冷笑话精选', result)
        result2 = list(yield_usernames(u'踩！大家一起来踩吧：【视频：120422 AKB48上海行 上海粉丝为AKB48加油VTR】 http://163.fm/MEwbnt5 （分享自 @优酷娱乐中心） http://163.fm/GNDL1TO'))
        self.assertIn(u'优酷娱乐中心', result2)
        result3 = list(yield_usernames(u'这功能太牛了，不得不用#十年体#赞美一下：我听到微软一个工程师讲述了这个故事。@微软中国'))
        self.assertIn(u'微软中国', result3)
        
    def test_yield_quotes(self):
        result = list(yield_quotes(u'好帅的五月天。我一直很喜欢的洒脱。//@冷笑话精选:都听过么？'))
        self.assertIn(u'都听过么？', result)
        result2 = list(yield_quotes(u'支持。 ||@就要返回顶部：支持这个呼吁！让他们贪了钱也没地方跑！ ||@刘植荣 支持，资助受迫害者。http://163.fm/PpCpXCT'))
        for term in (u'支持这个呼吁！让他们贪了钱也没地方跑！', u'支持，资助受迫害者。http://163.fm/PpCpXCT'):
            self.assertIn(term, result2)
            
    def test_yield_uris(self):
        result = list(yield_uris(u'支持，资助受迫害者。http://163.fm/PpCpXCT'))
        self.assertIn(u'http://163.fm/PpCpXCT', result)

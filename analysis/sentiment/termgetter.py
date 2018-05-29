#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os.path
import requests
import re
import itertools
import config.loader
import jianfan
import codecs

def get_terms():
    scrapped_terms = (term for func in term_scrapers for term in func() if len(term) > 1)
    #known_terms = (term for lexicon_type in known_filenames for term in get_terms_from_file(lexicon_type) if len(term) > 1)
    known_terms = []
    terms = itertools.chain.from_iterable([scrapped_terms, known_terms])
    return (jianfan.ftoj(term) for term in terms)

known_filenames = {
        'negative':'known_negative.txt',
        'positive':'known_positive.txt',
        'default':'known_emotions.txt',
        'idiom':'known_idioms.txt',
        'couch1':'known_terms.jieba.txt',
        'couch2':'known_terms.naive.txt',
    }
    
def get_terms_from_file(lexicon_type='default'):
    lexicon_type = lexicon_type if lexicon_type in known_filenames else 'default'
    filename = known_filenames.get(lexicon_type)
    file_path = os.path.join('sentiment','training',filename)
    logging.debug(u'Loading terms from file <{0}>'.format(filename))
    with codecs.open(file_path,'r+','utf8') as file:
        for line in file.readlines():
            yield line.strip()

smack_finder = re.compile(ur'<legend>(.+)</legend>',flags=(re.UNICODE))
def get_terms_from_chinasmack():
    def yield_cleaned_smack(smack):
        for splitter in (u'=',u',',u'，'):
            if splitter in smack:
                for smack_version in smack.split(splitter):
                    for clean_smack in yield_cleaned_smack(smack_version):
                        yield clean_smack
                raise StopIteration
        yield smack.strip()
        
    response = requests.get('http://www.chinasmack.com/glossary')
    for smack in smack_finder.findall(response.text):
        for clean_smack in yield_cleaned_smack(smack):
            yield clean_smack
    
lexicon_finder = re.compile(ur'<li>(.+)\s?\(<i',flags=(re.UNICODE))
cleaner = re.compile(ur'<[^<]*?>|，')
def get_terms_from_chinadigitaltimes():
    def yield_cleaned_lexicon(lexicon):
        if u'(' in lexicon or u')' in lexicon:
            raise StopIteration
        clean_lexicons = cleaner.sub(u' ',lexicon)
        for clean_lexicon in clean_lexicons.split():
            yield clean_lexicon.strip()
        
    response = requests.get('http://chinadigitaltimes.net/space/Grass-Mud_Horse_Lexicon_(arranged_alphabetically)')
    for lexicon in lexicon_finder.findall(response.text):
        for clean_lexicon in yield_cleaned_lexicon(lexicon):
            yield clean_lexicon
    
pos_pages = (
        u'http://zh.wiktionary.org/wiki/Category:%E6%B1%89%E8%AF%AD%E5%BD%A2%E5%AE%B9%E8%AF%8D',
        u'http://zh.wiktionary.org/wiki/Category:%E6%B1%89%E8%AF%AD%E5%8A%A8%E8%AF%8D',
        u'http://zh.wiktionary.org/wiki/Category:%E6%B1%89%E8%AF%AD%E6%88%90%E8%AF%AD',
    )
page_finder = re.compile(ur'<li>\s?<a href="/wiki/[%A-Z0-9]+" title="\w+">(\w+)</a>\s?</li>',flags=(re.UNICODE))
def get_terms_from_wiktionary():
    for pos_page in pos_pages:
        response = requests.get(pos_page)
        for page_name in page_finder.findall(response.text):
            yield page_name
    
term_scrapers = (
        get_terms_from_chinasmack,
#        get_terms_from_chinadigitaltimes,
#        get_terms_from_wiktionary
    )
    
def save_terms_from_couch(naive_tokens=False):
    tokenizer_index = int(naive_tokens)
    filename = known_filenames['couch'+str(tokenizer_index+1)]
    
    import calc.tokenize
    tokenizers = (calc.tokenize.tokenize_by_jieba, calc.tokenize.tokenize)
    
    import data.couch
    data.couch.get_db_env = lambda : config.loader.load('test-config.yaml').get('COUCH_ENV',{})
    
    import data.docs
    text = data.docs.get_all_docs_texts()
    terms = set(token for token,count in tokenizers[tokenizer_index](text).iteritems() if count > 1)
        
    file_path = os.path.join('sentiment','training',filename)
    with codecs.open(file_path,'w+','utf8') as file:
        file.write(u'\n'.join(terms))
        

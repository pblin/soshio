# -*- coding: utf-8 -*-
import json
import re
import collections
import random
import time
import urllib2
import datetime

import datetimes

from . import PlatformSearch, BlockedError, NoResultError
from .userinfo.sina_userinfo import SinaUserInfo
from . import jianfan
from .userinfo import utils
from .remote import get_url, WorkerError


class SinaSearch(PlatformSearch):
    name = "sina weibo"

    def next_query_time(self, post_count):
        if post_count > 5:
            return datetimes.now() + datetime.timedelta(minutes=random.randrange(0,2))
        else:
            return datetimes.now() + datetime.timedelta(
                    minutes=random.randrange(10, 20))

    def _search_keyword(self, keyword, historic, age_filter, post_filter):
        if historic:
            self._logger.info("Historic data retrieval has been disabled")
            raise StopIteration
        
        keyword = urllib2.quote(jianfan.ftoj(keyword).encode('utf-8'))
        self._logger.debug(
            'Requesting Sina for keyword <{0}>'.format(keyword))

        user_posts = collections.defaultdict(list)
        pages = [0]
        # random.shuffle(pages)
        for page in pages:  # Max 50 pages for weibo search
            try:
                self._logger.debug('Requesting page %d...' % (page + 1))
                if historic:
                    uri = 'http://s.weibo.com/wb/{0}&page={1}'.format(
                        keyword, page + 1)
                else:
                    uri = 'http://s.weibo.com/wb/{0}&xsort=time&Refer=STopic_box'.format(
                        keyword)
                uri = uri.encode('utf-8')
                for i in range(10):  # max retrires: 10 times
                    try:
                        html = get_url(uri)
                    except WorkerError:
                        if i == 10 - 1:
                            raise WorkerError("Max retries reached")
                        continue
                    else:
                        break

                next_page = True
                for post_info in self._scrape_posts(html):
                    if age_filter and age_filter(post_info.get('datetime')):
                        next_page = False
                        continue
                    if post_filter(post_info):
                        user_posts[post_info.pop('uid')].append(post_info)
            except BlockedError as e:
                self._logger.error(str(e))
                break
            except NoResultError as e:
                self._logger.info("No result for page %d" % (page + 1))
                break

            if not next_page and not historic:
                break
#            if br.find_link(u'下一页'):
#                time.sleep(random.randint(1, 5))
#            else:
#                break

        user_posts = SinaUserInfo().update_user_posts(user_posts)
        for uid, post_infos in user_posts.items():
            for post_info in post_infos:
                yield post_info

    _forward_finder = re.compile(
        ur'<dl class=\\"comment(.+?)<\\/dl>',
        flags=(re.UNICODE))
    _id_finder = re.compile(r'mid=\\"(\d+)\\" action-type')
    _date_finder = re.compile(r'date=\\"(\d+)\\" class=\\"date\\"')
    _user_finder = re.compile(ur'nick-name=\\"(.+?)\\"', flags=(re.UNICODE))
    _content_finder = re.compile(ur'<em>(.+?)<\\/em>', flags=(re.UNICODE))
    _repost_finder = re.compile(ur'\\u8f6c\\u53d1(\(\d+\))?')
    _comment_finder = re.compile(ur'\\u8bc4\\u8bba(\(\d+\))?')
    _post_finder = re.compile(
        ur'a href=\\"http:\\/\\/(weibo.com\\/\d+\\/\w+\\)" title')
    _uid_finder = re.compile(
        ur'a href=\\"http:\\/\\/weibo.com\\/(\d+)\\/\w+\\" title')
    _noresult_finder = re.compile(r'noresult_tit')

    @utils.cast_iter()
    def _scrape_posts(self, text):  # TODO: test!
        if self._noresult_finder.search(text):
            raise NoResultError()

        text = self._forward_finder.sub(u'', text)
        ids = self._id_finder.findall(text)
        dates = self._date_finder.findall(text)
        users = self._user_finder.findall(text)
        contents = self._content_finder.findall(text)
        reposts = self._repost_finder.findall(text)
        comments = self._comment_finder.findall(text)
        post_uris = self._post_finder.findall(text)
        uids = self._uid_finder.findall(text)
        
        for i, id in enumerate(ids):
            yield {
                'id': id,
                'datetime': int(dates[i]) / 1000,
                'username': self._json_to_unicode(users[i]),
                'uid': uids[i],
                'text': self._json_to_unicode(
                    self._clean_scraped_content(contents[i])),
                'shares': self._clean_scraped_stat(reposts[i]),
                'replies': self._clean_scraped_stat(comments[i]),
                'uri': post_uris[i].replace('\\', ''),
                'platform': self.name,
            }

        if len(ids) == 0:
            raise BlockedError("Blocked by sina!")

    _alt_finder = re.compile(ur'alt=\\"(.+?)\\"', flags=(re.UNICODE))
    _img_finder = re.compile(ur'<img[^<]*?>', flags=(re.UNICODE))
    _tag_finder = re.compile(ur'<[^<]*?>', flags=(re.UNICODE))

    def _clean_scraped_content(self, content):  # TODO: test!
        alts = self._alt_finder.findall(content)
        imgs = self._img_finder.findall(content)
        for i, img in enumerate(imgs):
            if i >= len(alts):
                break
            content = content.replace(img, alts[i])
        return self._tag_finder.sub(u'', content).strip()

    _digit_finder = re.compile(r'\d+')

    def _clean_scraped_stat(self, stat):
        digits = self._digit_finder.findall(stat)
        if digits:
            return int(digits[0])

    def _json_to_unicode(self, text):
        return json.loads(u'"{0}"'.format(text))

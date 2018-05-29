# -*- coding: utf-8 -*-
import json
import re
import collections
import random
import time
import urllib2
import HTMLParser
import pprint
import traceback
import datetime

import datetimes

from . import PlatformSearch, BlockedError, NoResultError
from .userinfo.sina_userinfo import SinaUserInfo
from . import jianfan
from .userinfo import utils
from .remote import get_url, WorkerError


class TencentSearch(PlatformSearch):
    name = "tencent weibo"

    def next_query_time(self, post_count):
        return datetimes.now() + datetime.timedelta(hours=3*random.randrange(10, 20)/10)

    def _search_keyword(self, keyword, historic, age_filter, post_filter):
        keyword = jianfan.ftoj(keyword).encode('utf-8')
        self._logger.debug(
            'Requesting YunYun(Tencent) for keyword <{0}>'.format(keyword))

        user_posts = collections.defaultdict(list)
        pages = range(10)
        for page in pages:  # Max 10  pages for yunyun search
            try:
                for retry in range(0, 5): # May retry up to 5 times if blocked
                    try:
                        self._logger.debug('Requesting page %d...' % (page + 1))
                        if historic:
                            #not supported yet
                            self._logger.warning("Historic data fetching is not supported for Tencent Weibo yet!")
                            raise StopIteration
                            break
                        else:
                            if page == 0:
                                uri = 'http://weibo.yunyun.com/Weibo.php?q={0}&wbts=1'.format(
                                    urllib2.quote("site:t.qq.com "+keyword))
                            else:
                                uri = 'http://weibo.yunyun.com/Weibo.php?p={1}&q={0}&wbts=1'.format(
                                    urllib2.quote("site:t.qq.com "+keyword), page+1)
                        #uri = uri.encode('utf-8')
                        for i in range(10):  # max retrires: 10 times
                            try:
                                html = get_url(uri, 'tencent_get_url')
                            except WorkerError:
                                if i == 10 - 1:
                                    raise WorkerError("Max retries reached")
                                continue
                            else:
                                break

                        #next_page = False
                        for post_info in self._scrape_posts(html):
                            #ignore age_filter for now
#                            if age_filter and age_filter(post_info.get('datetime')):
#                                continue
                            if post_filter(post_info):
                                user_posts[post_info.pop('uid')].append(post_info)
                                #next_page = True
                        break
                    except BlockedError as e:
                        if retry == 4:
                            self._logger.warning("<%s> %s for keyword %s on page %d" % (self.name, str(e), keyword, page+1))
                        continue
            except NoResultError as e:
                self._logger.info("No result for page %d with keyword %s" % (page+1, keyword))
                break

            #if not next_page and not historic:
            #    break

        #user_posts = SinaUserInfo().update_user_posts(user_posts)
        for uid, post_infos in user_posts.items():
            for post_info in post_infos:
                yield post_info

    data_finder = re.compile("displaySearchResult\\(_yrE\\(\\'searchtabContainer\\'\\), state,\s+(.*)\\);", flags=(re.UNICODE))
    id_finder = re.compile("\\/(\w+)$")
    uid_finder = re.compile("\\.com\\/(\S+)$")
    uri_finder = re.compile("http:\\/\\/(.+)")
    platform_finder = re.compile("http:\\/\\/(?:\w+\\.)*(\w+)\\.com")
    @utils.cast_iter()
    def _scrape_posts(self, html): # TODO: test!
        h = HTMLParser.HTMLParser()

        try:
            tmp = self.data_finder.search(html).group(1)
        except AttributeError as e:
#            self._logger.debug(html)
            raise BlockedError('Blocked by YunYun!')

        posts = json.loads(tmp)
        del tmp
        
        if len(posts[0]) == 0:
            raise NoResultError()

        for post in posts[0]:
            try:
                post = post[0]
                uri = self.uri_finder.search(post[0][0]).group(1)
                id = self.id_finder.search(uri).group(1)
                text = h.unescape(post[0][2])
                username = post[0][1]
                uid = self.uid_finder.search(post[0][4]).group(1)
                reposts = post[0][5]
                comments = post[0][6]
                p_datetime = post[2]
            except AttributeError as e:
                self._logger.debug(traceback.format_exc())
                self._logger.debug(pprint.PrettyPrinter().pformat(post[0][4]))
                continue
            except TypeError as e:
                self._logger.debug(traceback.format_exc())
                self._logger.debug(pprint.PrettyPrinter().pformat(post))
                raise NoResultError()

            yield {
                'id': id,
                'datetime': p_datetime,
                'username': username,
                'uid': uid,
                'text': self.clean_scraped_text(text),
                'shares': reposts if reposts else 0,
                'replies': comments if comments else 0,
                'uri': uri,
                'platform': self.name
                }

    tag_finder = re.compile(ur'<[^<]*?>',flags=(re.UNICODE))
    def clean_scraped_text(self, text): # TODO: test!
        """Remove tags in the text."""
        return self.tag_finder.sub(u'',text).strip()

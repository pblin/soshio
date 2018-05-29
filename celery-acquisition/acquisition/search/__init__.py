# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import logging
import itertools

from . import formator
from . import jianfan


class PlatformSearch():
    __metaclass__ = ABCMeta

    name = 'platform name'

    def __init__(self, logging_level='DEBUG'):
        self._logger = logging.getLogger(__name__)

    def search(self, query_obj, historic, age_filter):
        self._logger.info(
            u'Collecting data for query <%s> with keywords<%s> on platform <%s>' %
            (query_obj.query, ','.join(query_obj.keywords), self.name))

        results = []
        for keyword in query_obj.keywords:
            keyword = keyword.replace(u'\uff0e',".")
            self._logger.debug(
                u'Collecting data for keyword <{0}> on platform <{1}>'.format(keyword, self.name))
            results += list(
                self._search_keyword(keyword,
                                     historic,
                                     age_filter,
                                     self._get_matches_query(query_obj)))

        results = formator.map_results(query_obj.query, results)

        self._logger.info(
            u'Collected <{0}> posts for query <{1}> on platform {2}'.format(len(results),
                                                                            query_obj.query,
                                                                            self.name))
        return results

    @abstractmethod
    def next_query_time(self, post_count):
        pass

    @abstractmethod
    def _search_keyword(self, keyword):
        pass

    def _get_matches_query(self, query_obj):
        standardize = lambda text: jianfan.ftoj(text.lower())

        def matches_query(post):
            inputs = [standardize(arg) in standardize(post['text'])
                      for arg in query_obj.args]
            return query_obj.match(*inputs)
        return matches_query

#    def _filter_results(self, results):
#        filtered_results = filter(matches_query, results)
#        return filtered_results


class BlockedError(Exception):
    pass


class NoResultError(Exception):
    pass

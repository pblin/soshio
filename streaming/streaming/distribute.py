import logging

import jianfan

from data.posts import push
from data.subscriptions import SubscriptionManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_matches_query(query_obj):
    standardize = lambda text : jianfan.ftoj(text.lower())
    def matches_query(post):
        inputs = [standardize(arg) in standardize(post['text']) for arg in query_obj.args]
        return query_obj.match(*inputs)
    return matches_query
    

def distribute(keyword, post):
    for subscription in SubscriptionManager().get_subscriptions(keyword):
        q_obj = subscription.get_query_obj()
        matches_query = get_matches_query(q_obj)
        if matches_query(post):
            post['query']=q_obj.query
            push([post])
            logger.debug(u"Pushed 1 post to query %s" % q_obj.query)

import datetime
import random

import datetimes
#from requests.exceptions import HTTPError

from .data.subscriptions import Subscription, SubscriptionManager
from .data.posts import push
from . import get_celery, logger, get_platforms

celery = get_celery()
active_platforms = get_platforms()


# def catchHTTPError(original_function):
#    def new_function(*args, **kwargs):
#        try:
#            original_function(*args, **kwargs)
#        except HTTPError as e:
#            logger.warning(str(e))
#    return new_function


@celery.task
def fetch_historic_platform(query, platform):
    subscription = Subscription(query)
    manager = SubscriptionManager()

    if not subscription:
        logger.warning(
            u"%s not found in the subscription list. (Maybe have been deleted.)" %
            query)
        return

    if subscription.has_historic_data(platform):
        logger.debug(
            u"Already fetched historic from %s for %s. Skipping..." %
            (platform, query))
        return

    manager.mark_earliest_datetime(
        query,
        datetimes.now(),
        platform)  # lock the subscription
    results = active_platforms[platform](
    ).search(subscription.get_query_obj(), historic=True,
             age_filter=get_age_filter(subscription.get_created_datetime(), True))
    logger.info("Pushing results to SQS...")
    push(results)

    logger.info("Updating earlist_datetime...")
    e_datetime = None
    for d in [r['datetime'] for r in results]:
        if not e_datetime:
            e_datetime = d
            continue
        if e_datetime > d:
            e_datetime = d
    if e_datetime:
        manager.mark_earliest_datetime(
            query,
            datetimes.extract_datetime(e_datetime),
            platform)

    logger.info(u"Finished fetching historic %s from %s" % (query, platform))


@celery.task
def fetch_historic(query):
    for platform in active_platforms.keys():
        fetch_historic_platform.delay(query, platform)


@celery.task
def fetch_platform(query, platform):
    subscription = Subscription(query)
    manager = SubscriptionManager()

    logger.debug(u"Received request to fetch new posts for %s" % query)
    if not subscription.ready_for_next(platform):
        logger.debug(
            u"Not ready for next fetch(%s, %s). Skipping..." %
            (query, platform))
        return
    manager.mark_next_query_datetime(query, platform)  # lock the subscription
    results = active_platforms[platform](
    ).search(subscription.get_query_obj(), historic=False,
             age_filter=get_age_filter(subscription.get_latest_datetime(platform), historic=False))
    logger.debug("Pushing results to SQS...")
    push(results)

    logger.debug("Updating latest_datetime...")
    l_datetime = None
    for d in [r['datetime'] for r in results]:
        if not l_datetime:
            l_datetime = d
            continue
        if l_datetime < d:
            l_datetime = d
    if l_datetime:
        manager.mark_latest_datetime(
            query,
            datetimes.extract_datetime(l_datetime),
            platform)

    logger.debug("Updating next_query_datetime...")
    manager.mark_next_query_datetime(query, platform, 
                                     active_platforms[platform]().next_query_time(len(results)))

    logger.info(u"Finished fetching %s from %s" % (query, platform))


@celery.task
def fetch(query):
    for platform in active_platforms.keys():
        fetch_platform.delay(query, platform)


def get_age_filter(baseline_datetime, historic):
    if historic:
        def is_newer(p_datetime_str):
            p_datetime = datetimes.extract_datetime(p_datetime_str)
            return p_datetime >= baseline_datetime if p_datetime else False
        return is_newer
    else:
        def is_older(p_datetime_str):
            p_datetime = datetimes.extract_datetime(p_datetime_str)
#            logger.debug("%s, %s" % (p_datetime.isoformat(), (baseline_datetime - datetime.timedelta(minutes=5)).isoformat()))
            return p_datetime < (baseline_datetime - datetime.timedelta(minutes=5)) if p_datetime else False
        return is_older

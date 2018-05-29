from time import sleep, time
import logging

from acquisition import get_celery, get_platforms
from acquisition.data.subscriptions import SubscriptionManager, Subscription
from acquisition.tasks import fetch_platform

INTERVAL = 30  # secs

if __name__ == '__main__':
    logger = logging.getLogger(".")
    logger.setLevel(logging.DEBUG)
    celery = get_celery()
    active_platforms = get_platforms()
    while True:
        start_time = time()

        queries = SubscriptionManager().get_queries()
        logger.info("Total queries: %d" % len(queries))
        for query in queries:
            subscription = Subscription(query)
            for platform in active_platforms.keys():
                if subscription.ready_for_next(platform):
                    #logger.info(
                    #    u"Triggering fetching %s on %s" %
                    #    (query, platform))
                    fetch_platform.delay(query, platform)

        duration = time() - start_time

        if duration >= INTERVAL:
            continue

        logger.debug("sleep for %d seconds" % int(INTERVAL - duration))
        sleep(INTERVAL - duration)

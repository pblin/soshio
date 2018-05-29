import os
import logging
import urllib

#from celery.utils.log import get_task_logger
from celery import Celery
import iron_celery
from kombu import Exchange, Queue
import config.loader

from .search.sina import SinaSearch
from .search.tencent import TencentSearch
from .data.sqs import get_aws_env 

#logger = get_task_logger(__name__)
logger = logging.getLogger(__name__)

if os.environ.get('TEST'):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


def get_celery():
    aws_env = get_aws_env()
    #logger.debug(
    #    "Iron ENV %s:%s@%s" %
    #    (iron_env['project_id'], iron_env['token'], iron_env['host']))
    queue_name = config.loader.load().get('CELERY_QUEUE_NAME')
    logger.debug("Queue name: %s" % queue_name)
    celery = Celery(
        broker='sqs://%s:%s@' %
        (aws_env['key'], aws_env['secret']))
    celery.conf.update(
        CELERY_DEFAULT_QUEUE=queue_name,
        CELERY_QUEUES=(
            Queue(queue_name, Exchange('default'), routing_key='default'),
        ),
        CELERYD_HIJACK_ROOT_LOGGER = False,
        #        CELERYD_TASK_LOG_FORMAT = u'[%(levelname)s/%(processName)s][%(task_name)s] %(message)s',
        #        CELERYD_LOG_FORMAT = u'[%(levelname)s/%(processName)s] %(message)s',
        CELERYD_REDIRECT_STDOUT = False,
        CELERY_TASK_SERIALIZER = 'yaml',
        CELERY_ACCEPT_CONTENT = ['yaml'],
    )
    return celery


def get_platforms():
    active_platforms = {
        SinaSearch.name: SinaSearch,
#        TencentSearch.name: TencentSearch,
    }
    return active_platforms

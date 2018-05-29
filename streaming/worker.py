import logging

from pebble import ThreadPool

from streaming.data.socialgist import WeiboStream
from streaming.distribute import distribute

if __name__ == '__main__':
    logger = logging.getLogger("streaming")
    logger.setLevel(logging.DEBUG)
    stream = WeiboStream()
    with ThreadPool(workers=5) as tp:
        for keyword, post in stream.get_posts():
            tp.schedule(distribute, args=(keyword, post))

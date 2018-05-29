from abc import ABCMeta, abstractmethod
import logging


class PlatformUserInfo:
    __metaclass__ = ABCMeta

    def __init__(self, logging_level='DEBUG'):
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def _get_userinfo(self, uid):
        """Return gender, location, and follower count of the given user"""
        return

    @abstractmethod
    def update_user_posts(self, user_posts):
        """Add user info into post info. User_posts is a dictionary with keys of user id and values of posts posted by the user"""
        return

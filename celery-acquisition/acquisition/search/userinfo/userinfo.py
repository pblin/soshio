import collections

from .sina_userinfo import SinaUserInfo
from .tencent_userinfo import TencentUserInfo


class UserInfo():
    _userinfo = {
        'sina weibo': SinaUserInfo(),
        'tencent weibo': TencentUserInfo(),
    }

    def add_user_info(self, platform_posts):
        for platform, posts in platform_posts.items():
            user_posts = collections.defaultdict(list)
            for post in posts:
                user_posts[post.pop('uid')].append(post)
            if platform not in self._userinfo:
                continue
                # yield user_posts
            else:
                yield self._userinfo[platform].update_user_posts(user_posts)

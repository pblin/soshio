# -*- coding: utf-8 -*

import random
import logging

import requests

from . import PlatformUserInfo
from . import utils


class TencentUserInfo(PlatformUserInfo):

    _app_credentials = [  # TODO: migrate to OAuth2.0
        #name, app_key, app_secret, access_token, openid
        (u'RisingTide', '801058005', '31cc09205420a004f3575467387145a7',
         '6317e2f92761132c200451c220c9dd62', 'B40E9F89EB4E9ED97B4F9944117A26CB'),
    ]

    def _get_credential(self):
        _, app_key, app_secret, access_token, openid  = random.choice(self._app_credentials)
        return app_key, app_secret, access_token, openid

    _genders = [None, 'm', 'f']

    def _get_gender(self, num):
        return self._genders[num] if num < len(self._genders) else None

    def _get_userinfo(self, uid):
        """Get a single user's location information."""
        app_key, app_secret, access_token, openid = self._get_credential()
        data = {'format': 'json',
                'name': uid,
                'fopenid': '',
                'oauth_consumer_key': app_key,
                'oauth_version': '2.a',
                'scope': 'all',
                'clientip': '114.32.20.146',
                'openid': openid,
                'access_token': access_token }
        info = requests.get('http://open.t.qq.com/api/user/other_info', params=data).json()
        return uid, {
            'gender': self.get_gender(info['data']['sex']),
            'location': response.get('location')}
        
        
    def update_user_posts(self, user_posts):
        uids = user_posts.keys()
        sampled_uids = []  # Not implemented yet
        nonsampled_uids = set(uids).difference(sampled_uids)
        #user_infos = self._get_follower_count(nonsampled_uids)
        user_infos.update(filter(None, map(self._get_userinfo, sampled_uids)))

        for uid, post_infos in user_posts.items():
            for post_info in post_infos:
                post_info.update(user_infos.get(uid) or {})

        return user_posts

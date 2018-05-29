import random
import math

import requests

from . import PlatformUserInfo
from . import utils


class SinaUserInfo(PlatformUserInfo):
    _app_credentials = {
        (u'us@getsoshio.com', u'13ass@ssins'): [
            ('2037343500', 'c0b3eae41b81ed275b26b23f41bf01f8'),
            ('1223011909', '55147646f4bb49d78213ffbcc0011bf9'),
            ('1002922569', 'fac9ba6d9187d95b8074662b944c8cb5'),
        ],

        (u'whosbacon@gmail.com', u'analyzeTheWeb'): [
            ('409980230', '054ab84419d1cceff3d866874a7c1249'),
            ('1938791691', '4c0c14ff118c395fd26339cf7ded0742'),
            ('1238521281', 'c4b9b5b63cb67197636d2a553a87bab6'),
        ],

        (u'team@thinkudo.com', u'analyzeTheWeb'): [
            ('722506321', '919a2c0b0f604c2330a8e94034cbd141'),
            ('746277687', '10c8e66abb7b499e4e52df0eab7cb0c1'),
            ('2299258682', '9b83978c90d294951dcaf4905e4fb2b7'),
        ],
    }

    def _get_credential(self):
        credential = random.choice(self._app_credentials.keys())
        return credential, random.choice(self._app_credentials[credential])[0]

    @utils.cast_iter(cast=dict)
    def _get_follower_count(self, uids):
        """Get multiple users' follower counts. Max number of users per batch is 100."""
        if not uids:
            raise StopIteration
        credential, appkey = self._get_credential()
        for i in range(0, len(uids), 100):
            self._logger.debug("Getting follower counts from sina...")
            uri = u'https://api.weibo.com/2/users/counts.json?uids={0}&source={1}'.format(
                ','.join(uids[i:i + 100]), appkey)
            response = requests.get(uri, auth=credential).json()
            self._check_error(response)
            for result in response or []:
                yield str(result['id']), {'reach': result['followers_count']}

    def _check_error(self, response):
        if not response:
            raise StopIteration
        if 'error' in response and response['error']:
            self._logger.warning(
                'Received Sina error <{0}>'.format(response.get('error')))
            raise StopIteration

    def _get_userinfo(self, uid):
        credential, appkey = self._get_credential()
        self._logger.debug("Getting user info from sina...")
        uri = u'https://api.weibo.com/2/users/show.json?uid={0}&source={1}'.format(
            uid, appkey)
        response = requests.get(uri, auth=credential).json()
        try:
            self._check_error(response)
        except StopIteration:
            return
        return uid, {
            'gender': response.get('gender'),
            'location': response.get('location'),
            'reach': response.get('followers_count')
        }

    def update_user_posts(self, user_posts):
        uids = user_posts.keys()
        sampled_uids = random.sample(uids, int(math.floor(len(uids) / 50)))
        nonsampled_uids = set(uids).difference(sampled_uids)
        user_infos = {}
        try:
            user_infos = self._get_follower_count(list(nonsampled_uids))
        except Exception as e:
            self._logger.warning("Error fetching follower count: " + str(e))

        try:
            user_infos.update(
                filter(None, map(self._get_userinfo, sampled_uids)))
        except Exception as e:
            self._logger.warning("Error fetching user info: " + str(e))

        for uid, post_infos in user_posts.items():
            for post_info in post_infos:
                post_info.update(user_infos.get(uid) or {})

        return user_posts

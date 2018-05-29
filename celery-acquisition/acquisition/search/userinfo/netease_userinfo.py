import random

import t4py.tblog
import t4py.oauth

from . import PlatformUserInfo


class NeteaseUserInfo(PlatformUserInfo):
    _app_credentials = [
        #name, app_key, app_secret, access_token, token_secret
        (u'Thinkudo,談情', 'N2SxulMVk7QCOvHL', 'NJ0Ju3kp13Wvyl1CCoihj7htFR7lQJ9l',
         'e04c9a810bf5f11cc820f58d27a9f679', 'f2c30f55919e570c8ee58c2e6ab30f91'),
        (u'Thinkudo,Sentianalysis', 'Mu2qIXqh6njuSPe1', 'GTxCnmyNFDaWJXWjQNJG40dI7pRn4NOp',
         'ecc103f982b75b521e5bdc51e465f9ef', 'be4e35c5a979e91626d5a869502d22fc'),
        (u'Thinkudo,中文情感分析', 'TKuaxx6dGGgyJ1Mj', 'Ien4h8p0AewMrWcovsxrceS071PFC2uV',
         'cd313a5462e4ec31722c6b594ac9e393', 'e3b98206e4a68a706a7b7b2b1b46f69d'),
        (u'Thinkudo,社交數據分析', 'Y7fhlAKQVfuvFxs1', 'bwpziEJjRQdvljotwd38KbIknu3lVzQD',
         'c0fc31ac14acf89b061d5734def8eb6a', 'c22dd6e6875d4127416e70ea028ae6c8'),
        (u'Thinkudo,社交數據', 'KT5xCHL2bIhRCSjD', '0QbFiXebddVN0tN10Q40ghFugxsRUokl',
         'b60c8b12d44b6518c70ca1e637885133', 'b6193cbb6e9e0602c0d32536f7226b88'),
    ]

    def _get_credential(self):
        _, app_key, app_secret, access_token, token_secret = random.choice(
            _app_credentials)
        return app_key, app_secret, access_token, token_secret

    def _get_client(self):
        app_keu, app_secret, access_token, token_secret = self._get_credential
        client = t4py.tblog.TBlog(app_key, app_secret)
        client._request_handler.access_token = t4py.oauth.OAuthToken(
            access_token, token_secret)

#!/usr/bin/python
# -*- coding: utf-8 -*-

import data.users
import data.subscriptions

def run(interval):
    if interval == 'day':
        usernames= data.users.disable_expired_trial_users()
        data.subscriptions.remove_users_subscriptions(usernames)

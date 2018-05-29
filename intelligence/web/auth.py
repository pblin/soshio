#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import functools
import flask
import hashlib
import config.loader

def requires_auth(func):
    @functools.wraps(func)
    def auth_and_execute(*args, **kwargs):
        return func(*args, **kwargs) if authorize() else ask_credential()
    return auth_and_execute
    
def authorize():
    credential = flask.request.authorization
    if not credential: return False
    correct = config.loader.load().get('CREDENTIAL')
    return credential.username == correct.get('USERNAME') and secure_hash(credential.password) == correct.get('PASSWORD')
    
def ask_credential():
    response = flask.make_response('Access Denied', 401)
    response.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
    return response
    
def secure_hash(value):
    return hashlib.sha256(value).hexdigest()
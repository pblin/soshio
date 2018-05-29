#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import hashlib
import flask
import datetimes
import data.users
import data.subscriptions

def get_users():
    users = data.users.get_all_users()
    def to_dict(u):
        return {
                'username': u['_id'],
                'uri': flask.url_for('manage_user', username=u['_id']),
                'datetime': datetimes.to_timestamp(u['datetime']),
                'plan': u.get('plan',{}).get('name') or '',
                'disabled': u.get('disabled') or False
            }
    return flask.jsonify(users=map(to_dict, users))
    
def secure_hash(value):
    return hashlib.sha256(value).hexdigest()
    
def add_user(username):
    user = {'username':username}
    user_values = flask.request.form.to_dict()
    user['hashed_password'] = secure_hash(user_values.pop('password'))
    user['contact'] = get_contact_values(user_values)
    user['plan'] = get_plan_values(user_values)
    user['expiration_date'] = reset_expiration_date(user['plan'])
    if data.users.save_user(**user):
        return flask.jsonify(uri=flask.url_for('manage_user', username=username)), 201
    flask.abort(500)
    
def get_user(username):
    user = data.users.get_user(username)
    if not user: flask.abort(404)
    user.pop('_id')
    user.pop('hashed_password')
    user.update(get_restful_uris(username))
    if 'disabled_date' in user: user.pop('disabled_date') # legacy field
    for date_key in ('datetime','expiration_date'):
        if date_key not in user: continue
        user[date_key] = datetimes.to_timestamp(user[date_key])
    return flask.jsonify(**user)
    
def get_restful_uris(username):
    return {
            'index_uri': flask.url_for('manage_users'),
            'subscriptions_uri': flask.url_for('manage_subscriptions', username=username),
            'usages_uri': flask.url_for('get_usages', username=username),
            'consumptions_uri': flask.url_for('get_data_consumption', username=username)
        }
        
def default_user_update(username, **user_updates):
    if 'password' in user_updates and user_updates['password']:
        user_updates['hashed_password'] = secure_hash(user_updates.pop('password'))
    return data.users.update_user(username, **user_updates)
    
def activate_user(username, **user_updates):
    plan = get_plan_values(user_updates)
    return data.users.enable_user(username, new_plan=plan, expiration_date=expiration_date)
    
def enable_user(username):
    plan = data.users.get_user(username).get('plan')
    expiration_date = reset_expiration_date(plan)
    return data.users.enable_user(username, expiration_date=expiration_date)
    
update_actions = {
            'default': default_user_update,
            'activate': activate_user,
            'enable': enable_user,
            'disable': data.users.disable_user
        }
def update_user(username):
    username = username
    user_updates = flask.request.form.to_dict()
    if 'username' in user_updates: user_updates.pop('username')
    action = 'default' if 'action' not in user_updates else user_updates.pop('action')
    if update_actions[action](username, **user_updates):
        return flask.jsonify(uri=flask.url_for('manage_user', username=username))
    flask.abort(500)
    
def remove_user(username):
    if data.users.remove_user(username) and data.subscriptions.remove_subscriptions(username):
        return flask.jsonify(index_uri=flask.url_for('manage_users'))
    flask.abort(500)
    
def get_plan_values(params):
    return dict((key, params.get('plan.{0}'.format(key)) or '') for key in data.users.plan_fields)
    
def reset_expiration_date(plan):
    print plan
    if plan['name'] != 'trial': return
    return datetimes.get_datetime_ago(days=-14) # 2 weeks of trial
    
def get_contact_values(params):
    return dict((key, params.get('contact.{0}'.format(key)) or '') for key in data.users.contact_fields)
    
users_methods = {
        'GET': get_users
    }
    
user_methods = {
        'GET': get_user,
        'PUT': add_user,
        'POST': update_user,
        'DELETE': remove_user
    }
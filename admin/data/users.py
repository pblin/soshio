#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import datetimes
import mongo

def get_collection():
    return mongo.get_collection('users')
    
def get_user(username):
    with get_collection() as collection:
        return collection.find_one({'_id':username}) or {}
    
def save_user(username, hashed_password, contact, plan, expiration_date=None):
    user = {
            '_id': username,
            'username': username,
            'datetime': datetimes.now(),
            'hashed_password': hashed_password,
            'contact': contact,
            'plan': plan
        }
    if expiration_date: user['expiration_date'] = expiration_date
    with get_collection() as collection:
        return collection.insert(user, safe=True)
        
contact_fields = ('name','email','company','phone')
plan_fields = ('name','monthly','limit','overage')
    
def update_user(username, **sets):
    spec = {'_id': username}
    updates = {}
    if sets: updates['$set'] = sets
    with get_collection() as collection:
        return collection.update(spec, updates, safe=True)
    
def enable_user(username, new_plan=None, expiration_date=None):
    spec = {'_id': username}
    sets = {}
    if expiration_date: sets['expiration_date'] = expiration_date
    if new_plan: sets['plan'] = new_plan
    updates = {'$unset':{'disabled':1}, '$set':sets}
    with get_collection() as collection:
        return collection.update(spec, updates, safe=True)
        
def disable_user(username):
    spec = {'_id': username}
    return disable_users(spec)

def disable_expired_trial_users():
    spec = {
        'expiration_date':{'$lte':datetimes.now()},
        'plan.name':'trial',
        '$or': [
            {'disabled':False},
            {'disabled':{'$exists':False}}
        ]
    }
    with get_collection() as collection:
        usernames = [user['_id'] for user in collection.find(spec)]
    if not usernames: return
    disable_users(spec)
    return usernames
    
def disable_users(spec):
    updates = {
            '$set': {
                'disabled':True,
            }
        }
    with get_collection() as collection:
        return collection.update(spec, updates, multi=True, safe=True)
        
def remove_user(username):
    with get_collection() as collection:
        return collection.remove({'_id': username}, safe=True)
        
def get_all_active_users():
    spec = {
            '$or': [
                {'disabled':False},
                {'disabled':{'$exists':False}}
            ]
        }
    return get_all_users(spec=spec)
        
def get_all_users(spec=None, fields=None):
    spec = spec or {}
    fields = fields
    with get_collection() as collection:
        return collection.find(spec, fields)
    
#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import flask
import urllib2
import datetimes
import data.subscriptions
import data.usages
import queryparser

def get_subscriptions(username):
    def to_dict(subscription):
        query = subscription.get('query') or subscription.get('keyword') or ''
        return {
                'query': query,
                'uri': get_subscription_uri(username, query),
                'datetime': datetimes.to_timestamp(subscription['datetime']),
                'description': (subscription.get('description') or ''),
                'tags': subscription.get('tags') or ''
            }
    current = data.subscriptions.get_subscriptions(username)
    past = get_past_subscriptions(username, current)
    return flask.jsonify(current=map(to_dict, current), past=list(past))
    
def get_past_subscriptions(username, current=None):
    current = set(current or [])
    history = data.usages.get_past_subscriptions(username)
    for query in (set(history) - current):
        # TODO: determine subscription start and stop time
        yield {'query': query, 'username':username}
    
def add_subscription(username, query):
    return update_subscription(username, query), 201
    
def get_subscription(username, query):
    subscription = data.subscriptions.get_subscription(username, query)
    if not subscription: flask.abort(404)
    subscription_dict = {
            'query': subscription.get('query') or subscription.get('keyword') or '',
            'datetime': datetimes.to_timestamp(subscription['datetime']),
            'description': subscription.get('description'),
            'tags': subscription.get('tags') or ''
        }
    return flask.jsonify(**subscription_dict)
    
def update_subscription(username, query):
    details = flask.request.form.to_dict()
    if upsert_subscription(username, query, **details):
        return flask.jsonify(uri=get_subscription_uri(username, query))
    flask.abort(500)
    
def remove_subscriptions(username, query=None):
    if data.subscriptions.remove_subscriptions(username, query):
        return flask.jsonify(index_uri=flask.url_for('manage_subscriptions', username=username))
    flask.abort(500)
    
def upsert_subscription(username, query, description=None, platforms=None, tags=None):
    query = clean_query(query)
    details = parse_query(query)
    if description: details['description'] = description
    if tags: details['tags'] = list(tag.strip() for tag in tags.split(u',') if tag)
    if platforms: details['platforms'] = platforms.split(u';')
    return data.subscriptions.save_subscription(username, query, **details)
    
def parse_query(query):
    evalable, keywords = queryparser.create_query_lambda(query)
    min_keywords = queryparser.get_keywords_needed(query)
    return {
            'keywords': dict((keyword, datetimes.get_datetime_ago(hours=1)) for keyword in min_keywords),
            'match_func': {
                    'args': keywords,
                    'lambda': evalable
                }
        }
    
def get_subscription_uri(username, query):
    uri = flask.url_for('manage_subscription', username=username, query=query)
    return urllib2.unquote(uri)
    
def clean_query(query):
    query = query.replace('\n',' ')
    query = u' '.join(query.split())
    return query
    
subscriptions_methods = {
        'GET': get_subscriptions,
        'DELETE': remove_subscriptions
    }
    
subscription_methods = {
        'GET': get_subscription,
        'PUT': add_subscription,
        'POST': update_subscription,
        'DELETE': remove_subscriptions
    }

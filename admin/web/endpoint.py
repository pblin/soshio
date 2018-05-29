#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import urllib2
import os

import flask
from flask_sslify import SSLify

import auth
import users
import subscriptions
import usages
import feeds

app = flask.Flask(__name__)
app.secret_key = u'聽不見聽不見'.encode('utf-8')
if 'DYNO' in os.environ: # only trigger SSLify if the app is running on Heroku
    sslify = SSLify(app)

def run(port=5007, debug=False):
    app.run('0.0.0.0', port=port, debug=debug)

##### pages #####

@app.route(u'/', methods=['GET'])
@auth.requires_auth
def index():
    return flask.render_template('index.html')
    
@app.route(u'/users', methods=['GET'])
@auth.requires_auth
def users_manager():
    return flask.render_template('users.html')
    
@app.route(u'/environment', methods=['GET'])
@auth.requires_auth
def environment_monitor():
    return flask.render_template('environment.html')
    
##### services #####

@app.route(u'/services/users', methods=users.users_methods.keys())
@auth.requires_auth
def manage_users():
    return users.users_methods[flask.request.method]()

@app.route(u'/services/users/<username>', methods=users.user_methods.keys())
@auth.requires_auth
def manage_user(username):
    username = urllib2.unquote(username)
    return users.user_methods[flask.request.method](username)
    
@app.route(u'/services/users/<username>/subscriptions', methods=subscriptions.subscriptions_methods.keys())
@auth.requires_auth
def manage_subscriptions(username):
    username = urllib2.unquote(username)
    return subscriptions.subscriptions_methods[flask.request.method](username)
    
@app.route(u'/services/users/<username>/subscriptions/<query>', methods=subscriptions.subscription_methods.keys())
@auth.requires_auth
def manage_subscription(username, query):
    username = urllib2.unquote(username)
    query = subscriptions.clean_query(query)
    return subscriptions.subscription_methods[flask.request.method](username, query)
    
@app.route(u'/services/users/<username>/usages', methods=['GET'])
@auth.requires_auth
def get_usages(username):
    username = urllib2.unquote(username)
    try:
        user_usages = usages.get_usages(username)
    except TypeError, error:
        logging.info(u'No usages found for <{0}>'.format(username))
        user_usages = {}
    return flask.jsonify(usages=user_usages)
    
@app.route(u'/services/users/<username>/usages/consumption', methods=['GET'])
@auth.requires_auth
def get_data_consumption(username):
    username = urllib2.unquote(username)
    consumptions = usages.get_consumption(username)
    return flask.jsonify(consumptions=consumptions)
    
@app.route(u'/services/feeds', methods=['GET'])
@auth.requires_auth
def get_feeds():
    throughput = feeds.get_throughput()
    return flask.jsonify(throughput=throughput)

@app.route(u'/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

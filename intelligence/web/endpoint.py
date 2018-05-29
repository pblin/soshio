#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os

import flask
from iron_cache import IronCache
import config.loader
from celery import Celery
import iron_celery
from kombu import Exchange, Queue

import auth
from cache_control import nocache

def get_iron_env(host=True):
    mq_env = config.loader.load().get('MQ_ENV', {})
    if host:
        return{"project_id": mq_env['PROJECT'], "token": mq_env['TOKEN'], "host": mq_env.get("HOST","")}
    else:
        return{"project_id": mq_env['PROJECT'], "token": mq_env['TOKEN']}

def make_celery(app):
    iron_env = get_iron_env()
    logging.debug(
        "Iron ENV %s:%s@%s" %
        (iron_env['project_id'], iron_env['token'], iron_env['host']))
    #print iron_env
    queue_name = 'intelligence'
    celery = Celery(
        app.import_name,
        broker='ironmq://%s:%s@%s' %
        (iron_env['project_id'], iron_env['token'], iron_env['host']),
        backend='ironcache://%s:%s@/intelligence' %
        (iron_env['project_id'], iron_env['token']))
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = flask.Flask(__name__, static_path='')
app.secret_key = u'聽不到看不見'.encode('utf-8')
app.config.update(
    CELERY_DEFAULT_QUEUE='intelligence',
    CELERY_QUEUES=(
        Queue('intelligence', routing_key='default'),
        Queue('export'),
    ),
    CELERYD_REDIRECT_STDOUT = False,
    CELERY_TASK_SERIALIZER = 'yaml'
)
celery = make_celery(app)
cache = IronCache(**get_iron_env(host=False))

def get_app():
    return app

import report.endpoint
   
@app.route(u'/')
def root():
    return 'You talkin\' to me? You talkin\' to me? You talkin\' to me? Then who the hell else are you talking... you talking to me? Well I\'m the only one here. Who the fuck do you think you\'re talking to? Oh yeah? \'kay.'
    
@app.route(u'/<section>/<query>/<start>.<end>.json', methods=['GET'])
@auth.requires_auth
@nocache
def reports(**params):
    result = report.endpoint.execute(params) or {}
    return flask.jsonify(**result)
    
@app.route(u'/explore/<query>/<start>.<end>.json', methods=['GET'])
@auth.requires_auth
def explore(**params):
    params.update(flask.request.args)
    result = report.endpoint.explore(params) or {}
    return flask.jsonify(**result)
    
@app.route(u'/explore/details/<post_id>.json', methods=['GET','POST'])
@auth.requires_auth
def detail(**params):
    if flask.request.method == 'POST':
        params.update(flask.request.form.to_dict())
    result = report.endpoint.detail(params)
    return flask.jsonify(**result)
    
@app.route(u'/export/<query>/<start>.<end>.csv', methods=['GET'])
@auth.requires_auth
@nocache
def export(**params):
    params.update(flask.request.args)
    result = report.endpoint.export(params) # NOTE: may result in large stream that blocks the web process...
    return flask.jsonify(**result)
    #return flask.Response(result, mimetype=u'text/csv')

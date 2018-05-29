#!/usr/bin/python
# -*- coding: utf-8 -*-

import reporter
import explorer
import exporter
import detailer
import data.analyses

def export(params):
    return exporter.create(**params)
    
def execute(params):
    return reporter.create(**params)
    
def explore(params):
    return explorer.create(**params)
    
def detail(params):
    mode = params.pop('update') if 'update' in params else 'get'
    return detailer.execute(mode, **params)
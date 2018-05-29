#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import logging
import caching

BASE_URI = u'http://maps.googleapis.com/maps/api/geocode/json'

def search_locations(name):
    response = requests.get(BASE_URI + u'?address={0}&sensor=true'.format(name)).json()
    return response.get('results') or []

@caching.cached(timeout=3600 * 24)
def get_location(name):
    results = search_locations(name)
    if not results:
        logging.warning(u'Cannot find geo info for location <{0}>'.format(name))
        return
    location = results[0]
    english = location['address_components'][0]['long_name']
    english = english.replace('Railway Station','').strip()
    return english, location['geometry']['location']

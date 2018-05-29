#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import argparse
import background.endpoint
    
if __name__ == '__main__':
    reload(logging)
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Launches one-off historic data recollection')
    parser.add_argument('username', metavar='U', type=unicode, help='Username')
    parser.add_argument('hours', metavar='H', type=int, help='Hours to backtrack')
    args = parser.parse_args()
    background.endpoint.recollect_historical_data(args.username, hours=args.hours)

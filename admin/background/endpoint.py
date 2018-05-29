#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import trial
import consumptions

def run(interval):
    run_jobs(interval)
    if interval == 'day':
        check_longer_intervals()
        
def run_jobs(interval):
    trial.run(interval)
    consumptions.run(interval)
    
interval_checkers = {
        'month':lambda dt: dt.day == 1,
        'year':lambda dt: dt.month == 1 and dt.day == 1,
    }
    
def check_longer_intervals():
    now = datetime.datetime.utcnow()
    for interval, checker in interval_checkers.items():
        if not checker(now): continue
        run_jobs(interval)

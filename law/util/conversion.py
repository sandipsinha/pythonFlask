"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
import time

def to_js_time( d ):
    return int(time.mktime(d.timetuple())) * 1000

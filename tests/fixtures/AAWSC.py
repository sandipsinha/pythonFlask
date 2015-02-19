"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb import AAWSC

MODEL = AAWSC
FIXTURES = [
# Cust 1001
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 4, 8 ),
    'subdomain' : 'touchbiztest',
    'stNam'     : 'SUT',
    'trate'     : 0,
    'frate'     : 0,
    'tPlan'     : 1,
    'tGB'       : 0,
    'tDays'     : 15,
},
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 5, 8 ),
    'subdomain' : 'touchbiztest',
    'stNam'     : 'TWF',
    'trate'     : 0,
    'frate'     : 0,
    'tPlan'     : 2,
    'tGB'       : 200000000,
    'tDays'     : 7,
},
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 6, 8 ),
    'subdomain' : 'touchbiztest',
    'stNam'     : 'FWP',
    'trate'     : 49,
    'frate'     : 0,
    'tPlan'     : 3,
    'tGB'       : 1000000000,
    'tDays'     : 7,
},
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 6, 10 ),
    'subdomain' : 'touchbiztest',
    'stNam'     : 'FWU',
    'trate'     : 99,
    'frate'     : 49,
    'tPlan'     : 4,
    'tGB'       : 2000000000,
    'tDays'     : 15,
},
# Cust 1001
{
    'acct_id'   : 1001,
    'updated'   : datetime( 2014, 12, 2, 10 ),
    'subdomain' : 'touchbiztest2',
    'stNam'     : 'SUT',
    'trate'     : 0,
    'frate'     : 0,
    'tPlan'     : 1,
    'tGB'       : 0,
    'tDays'     : 15,
},
{
    'acct_id'   : 1001,
    'updated'   : datetime( 2014, 12, 25, 13 ),
    'subdomain' : 'touchbiztest2',
    'stNam'     : 'TWP',
    'trate'     : 99,
    'frate'     : 0,
    'tPlan'     : 4,
    'tGB'       : 100000000,
    'tDays'     : 15,
},
{
    'acct_id'   : 1001,
    'updated'   : datetime( 2015, 1, 2, 11 ),
    'subdomain' : 'touchbiztest2',
    'stNam'     : 'TWP',
    'trate'     : 99,
    'frate'     : 99,
    'tPlan'     : 4,
    'tGB'       : 1000000000,
    'tDays'     : 15,
},
# Cust 1002
{
    'acct_id'   : 1002,
    'updated'   : datetime( 2014, 4, 8 ),
    'subdomain' : 'touchbiztest3',
    'stNam'     : 'SUT',
    'trate'     : 0,
    'frate'     : 0,
    'tPlan'     : 1,
    'tGB'       : 0,
    'tDays'     : 15,
},
{
    'acct_id'   : 1002,
    'updated'   : datetime( 2014, 9, 22, 1 ),
    'subdomain' : 'touchbiztest3',
    'stNam'     : 'SUT',
    'trate'     : 49,
    'frate'     : 0,
    'tPlan'     : 3,
    'tGB'       : 1000000000,
    'tDays'     : 7,
},
# Cust 1004 -- Sub State Migration
{
    'acct_id'   : 1004,
    'updated'   : datetime( 2014, 10, 1 ),
    'subdomain' : 'touchbiztest3',
    'stNam'     : 'SUT',
    'trate'     : 0,
    'frate'     : 0,
    'tPlan'     : 1,
    'tGB'       : 0,
    'tDays'     : 15,
},
{
    'acct_id'   : 1004,
    'updated'   : datetime( 2014, 10, 20 ),
    'subdomain' : 'touchbiztest3',
    'stNam'     : 'TWP',
    'trate'     : 49,
    'frate'     : 0,
    'tPlan'     : 3,
    'tGB'       : 1000000000,
    'tDays'     : 7,
},
{
    'acct_id'   : 1004,
    'updated'   : datetime( 2015, 1, 6 ),
    'subdomain' : 'touchbiztest3',
    'stNam'     : 'PWF',
    'trate'     : 0,
    'frate'     : 49,
    'tPlan'     : 2,
    'tGB'       : 200000000,
    'tDays'     : 7,
},
]

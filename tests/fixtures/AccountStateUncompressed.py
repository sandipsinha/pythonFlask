"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb import AccountStateUncompressed

MODEL = AccountStateUncompressed
FIXTURES = [
# Cust 1001
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 4, 8 ),
    'subdomain' : 'touchbiztest',
    'state'     : 'SUT',
    'tRate'     : 0,
    'fRate'     : 0,
    'tPlan_id'  : 1,
    'tGB'       : 0,
    'tDays'     : 15,
},
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 5, 8 ),
    'subdomain' : 'touchbiztest',
    'state'     : 'TWF',
    'tRate'     : 0,
    'fRate'     : 0,
    'tPlan_id'  : 2,
    'tGB'       : 200000000,
    'tDays'     : 7,
},
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 6, 8 ),
    'subdomain' : 'touchbiztest',
    'state'     : 'FWP',
    'tRate'     : 49,
    'fRate'     : 0,
    'tPlan_id'  : 3,
    'tGB'       : 1000000000,
    'tDays'     : 7,
},
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 6, 10 ),
    'subdomain' : 'touchbiztest',
    'state'     : 'FWU',
    'tRate'     : 99,
    'fRate'     : 49,
    'tPlan_id'  : 4,
    'tGB'       : 2000000000,
    'tDays'     : 15,
},
# Cust 1001
{
    'acct_id'   : 1001,
    'updated'   : datetime( 2014, 12, 2, 10 ),
    'subdomain' : 'touchbiztest2',
    'state'     : 'SUT',
    'tRate'     : 0,
    'fRate'     : 0,
    'tPlan_id'  : 1,
    'tGB'       : 0,
    'tDays'     : 15,
},
{
    'acct_id'   : 1001,
    'updated'   : datetime( 2014, 12, 25, 13 ),
    'subdomain' : 'touchbiztest2',
    'state'     : 'TWP',
    'tRate'     : 99,
    'fRate'     : 0,
    'tPlan_id'  : 4,
    'tGB'       : 100000000,
    'tDays'     : 15,
},
{
    'acct_id'   : 1001,
    'updated'   : datetime( 2015, 1, 2, 11 ),
    'subdomain' : 'touchbiztest2',
    'state'     : 'TWP',
    'tRate'     : 99,
    'fRate'     : 99,
    'tPlan_id'  : 4,
    'tGB'       : 1000000000,
    'tDays'     : 15,
},
# Cust 1002
{
    'acct_id'   : 1002,
    'updated'   : datetime( 2014, 4, 8 ),
    'subdomain' : 'touchbiztest3',
    'state'     : 'SUT',
    'tRate'     : 0,
    'fRate'     : 0,
    'tPlan_id'  : 1,
    'tGB'       : 0,
    'tDays'     : 15,
},
{
    'acct_id'   : 1002,
    'updated'   : datetime( 2014, 9, 22, 1 ),
    'subdomain' : 'touchbiztest3',
    'state'     : 'SUT',
    'tRate'     : 49,
    'fRate'     : 0,
    'tPlan_id'  : 3,
    'tGB'       : 1000000000,
    'tDays'     : 7,
},
]

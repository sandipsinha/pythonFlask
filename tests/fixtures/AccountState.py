"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb import AccountState

MODEL = AccountState
FIXTURES = [
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 4, 8 ),
    'subdomain' : 'touchbiztest',
    'state'     : 'SUT',
    'tRate'     : '0',
    'fRate'     : '0',
    'tPlan_id'  : '1',
    'tGB'       : '0',
    'tDays'     : '15',
},
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 5, 8 ),
    'subdomain' : 'touchbiztest',
    'state'     : 'TWF',
    'tRate'     : '0',
    'fRate'     : '0',
    'tPlan_id'  : '2',
    'tGB'       : '200000000',
    'tDays'     : '7',
},
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 6, 8 ),
    'subdomain' : 'touchbiztest',
    'state'     : 'FWP',
    'tRate'     : '0',
    'fRate'     : '49',
    'tPlan_id'  : '3',
    'tGB'       : '1000000000',
    'tDays'     : '7',
},
{
    'acct_id'   : 1000,
    'updated'   : datetime( 2014, 6, 10 ),
    'subdomain' : 'touchbiztest',
    'state'     : 'FWU',
    'tRate'     : '0',
    'fRate'     : '99',
    'tPlan_id'  : '4',
    'tGB'       : '2000000000',
    'tDays'     : '15',
},
]

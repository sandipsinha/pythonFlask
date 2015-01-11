"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb import Account

MODEL = Account
FIXTURES = [
{
    'acct_id'       : 1000,
    'id'            : 958,
    'deployment'    : 'chopper',
    'legacy'        : 0,
    'created'       : datetime( 2014, 4, 8 ),
    'subdomain'     : 'touchbiztest',
    'email'         : 'touchbiztest@loggly.com',
    'phone'         : '858-335-3341',
    'zip'           : '92131',
    'is_test'       : False,
},
{
    'acct_id'       : 1001,
    'id'            : 999,
    'deployment'    : 'chopper',
    'legacy'        : 0,
    'created'       : datetime( 2014, 12, 15 ),
    'subdomain'     : 'touchbiztest2',
    'email'         : 'touchbiztest2@loggly.com',
    'phone'         : '858-335-3341',
    'zip'           : '92131',
    'is_test'       : False,
},
]

"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb_touchbiz import Touchbiz

MODEL = Touchbiz
FIXTURES = [
{
    'acct_id'       : 1000,
    'sales_rep_id'  : 2,
    'created'       : datetime( 2014, 5, 9 ),
    'modified'      : datetime( 2014, 5, 9 ),
    'tier'          : 'Development',
    'retention'     : 7,
    'volume'        : 100000000000,
    'sub_rate'      : 49,
    'billing_period': 'monthly',
},
{
    'acct_id'       : 1001,
    'sales_rep_id'  : 2,
    'created'       : datetime( 2014, 12, 15 ),
    'modified'      : datetime( 2014, 12, 15 ),
    'tier'          : 'Development',
    'retention'     : 7,
    'volume'        : 100000000000,
    'sub_rate'      : 49,
    'billing_period': 'monthly',
},
{
    'acct_id'       : 1001,
    'sales_rep_id'  : 3,
    'created'       : datetime( 2014, 12, 25, 3 ),
    'modified'      : datetime( 2014, 12, 25, 3 ),
    'tier'          : 'Production',
    'retention'     : 15,
    'volume'        : 100000000000,
    'sub_rate'      : 99,
    'billing_period': 'annual',
},
{
    'acct_id'       : 1001,
    'sales_rep_id'  : 3,
    'created'       : datetime( 2015, 2, 10, 15 ),
    'modified'      : datetime( 2015, 2, 10, 15 ),
    'tier'          : 'Production',
    'retention'     : 15,
    'volume'        : 200000000000,
    'sub_rate'      : 109,
    'billing_period': 'annual',
},
{
    'acct_id'       : 1002,
    'sales_rep_id'  : 2,
    'created'       : datetime( 2015, 2, 10, 15 ),
    'modified'      : datetime( 2015, 2, 10, 15 ),
    'tier'          : 'Production',
    'retention'     : 15,
    'volume'        : 200000000000,
    'sub_rate'      : 109,
    'billing_period': 'annual',
},
]

"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.touchbizdb import Touchbiz

MODEL = Touchbiz
FIXTURES = [
{
    'acct_id'       : 1000,
    'sales_rep_id'  : 2, # Angela
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
    'sales_rep_id'  : 2, # Angela
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
    'sales_rep_id'  : 3, # Steph
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
    'sales_rep_id'  : 3, # Steph
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
    'sales_rep_id'  : 2, # Angela
    'created'       : datetime( 2015, 2, 10, 15 ),
    'modified'      : datetime( 2015, 2, 10, 15 ),
    'tier'          : 'Production',
    'retention'     : 15,
    'volume'        : 200000000000,
    'sub_rate'      : 109,
    'billing_period': 'annual',
},
{
    'acct_id'       : 1003,
    'sales_rep_id'  : 2, # Angela
    'created'       : datetime( 2014, 4, 10 ),
    'modified'      : datetime( 2014, 4, 10 ),
    'tier'          : 'Production',
    'retention'     : 7,
    'volume'        : 100000000000,
    'sub_rate'      : 49,
    'billing_period': 'monthly',
},
{
    'acct_id'       : 1003,
    'sales_rep_id'  : 2, # Angela
    'created'       : datetime( 2015, 2, 10 ),
    'modified'      : datetime( 2015, 2, 10 ),
    'tier'          : 'Development',
    'retention'     : 7,
    'volume'        : 100000000000,
    'sub_rate'      : 49,
    'billing_period': 'monthly',
},
{
    'acct_id'       : 1010,
    'sales_rep_id'  : 2, # Angela
    'created'       : datetime( 2015, 3, 1 ),
    'modified'      : datetime( 2015, 3, 1 ),
    'tier'          : 'Development',
    'retention'     : 7,
    'volume'        : 100000000000,
    'sub_rate'      : 49,
    'billing_period': 'monthly',
},
{
    'acct_id'       : 1010,
    'sales_rep_id'  : 3, # Steph
    'created'       : datetime( 2015, 3, 22 ),
    'modified'      : datetime( 2015, 3, 22 ),
    'tier'          : 'Production',
    'retention'     : 15,
    'volume'        : 7000000000,
    'sub_rate'      : 349,
    'billing_period': 'monthly',
},
]

"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb import AccountActivity

MODEL = AccountActivity
FIXTURES = [
# Cust 1001
{
    'acct_id'         : 1000,
    'updated'         : datetime( 2014, 4, 8 ),
    'to_sub_rate'     : 0,
    'from_sub_rate'   : 0,
    'to_plan_id'      : 1,
    'to_vol_bytes'    : 0,
    'to_ret_days'     : 15,
},
{
    'acct_id'         : 1000,
    'updated'         : datetime( 2014, 5, 8 ),
    'to_sub_rate'     : 0,
    'from_sub_rate'   : 0,
    'to_plan_id'      : 2,
    'to_vol_bytes'    : 200000000,
    'to_ret_days'     : 7,
},
{
    'acct_id'         : 1000,
    'updated'         : datetime( 2014, 6, 8 ),
    'to_sub_rate'     : 49,
    'from_sub_rate'   : 0,
    'to_plan_id'      : 3,
    'to_vol_bytes'    : 1000000000,
    'to_ret_days'     : 7,
},
{
    'acct_id'         : 1000,
    'updated'         : datetime( 2014, 6, 10 ),
    'to_sub_rate'     : 99,
    'from_sub_rate'   : 49,
    'to_plan_id'      : 4,
    'to_vol_bytes'    : 2000000000,
    'to_ret_days'     : 15,
},
# Cust 1001
{
    'acct_id'         : 1001,
    'updated'         : datetime( 2014, 12, 2, 10 ),
    'to_sub_rate'     : 0,
    'from_sub_rate'   : 0,
    'to_plan_id'      : 1,
    'to_vol_bytes'    : 0,
    'to_ret_days'     : 15,
},
{
    'acct_id'         : 1001,
    'updated'         : datetime( 2014, 12, 25, 13 ),
    'to_sub_rate'     : 99,
    'from_sub_rate'   : 0,
    'to_plan_id'      : 4,
    'to_vol_bytes'    : 100000000,
    'to_ret_days'     : 15,
},
{
    'acct_id'         : 1001,
    'updated'         : datetime( 2015, 1, 2, 11 ),
    'to_sub_rate'     : 99,
    'from_sub_rate'   : 99,
    'to_plan_id'      : 4,
    'to_vol_bytes'    : 1000000000,
    'to_ret_days'     : 15,
},
# Cust 1002
{
    'acct_id'         : 1002,
    'updated'         : datetime( 2014, 4, 8 ),
    'to_sub_rate'     : 0,
    'from_sub_rate'   : 0,
    'to_plan_id'      : 1,
    'to_vol_bytes'    : 0,
    'to_ret_days'     : 15,
},
{
    'acct_id'         : 1002,
    'updated'         : datetime( 2014, 9, 22, 1 ),
    'to_sub_rate'     : 49,
    'from_sub_rate'   : 0,
    'to_plan_id'      : 3,
    'to_vol_bytes'    : 1000000000,
    'to_ret_days'     : 7,
},
]

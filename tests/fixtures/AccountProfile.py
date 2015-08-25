"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb import AccountProfile

MODEL = AccountProfile
FIXTURES = [
{
    'acct_id'    : 1000,
    'usercount'  : 5,
    'groupcount' : 7,
    'rulescount' : 9,
},
{
    'acct_id'    : 1001,
    'usercount'  : 7,
    'groupcount' : 5,
    'rulescount' : 2,
},
{
    'acct_id'    : 1002,
    'usercount'  : 3,
    'groupcount' : 2,
    'rulescount' : 1,
}
]

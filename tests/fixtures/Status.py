"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb import Status

MODEL = Status
FIXTURES = [
{
    'created'    : datetime( 2015, 1, 8 ),
    'acct_id'    : 1000,
    'subdomain'   : 'hollywood.com',
},
{
    'created'    : datetime( 2015, 2, 10 ),
    'acct_id'    : 1001,
    'subdomain'   : 'gifted.sportsperson',
},
{
    'created'    : datetime( 2015, 3, 12 ),
    'acct_id'    : 1002,
    'subdomain'   : 'talented.scientist',
},
{
    'created'    : datetime( 2015, 4, 10 ),
    'acct_id'    : 1003,
    'subdomain'   : 'crafty.politicians',
}
]

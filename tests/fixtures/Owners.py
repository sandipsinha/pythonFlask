"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb import Owners

MODEL = Owners
FIXTURES = [
{
    'acct_id'    : 1000,
    'subdomain'  : 'touchbiztest',
    'owner'      : 'Angela Eichner',
    'start_date' : datetime( 2014, 4, 8 ),
    'end_date'   : datetime( 2014, 4, 9 ),
    'executive'  : 0,
},
{
    'acct_id'    : 1000,
    'subdomain'  : 'touchbiztest',
    'owner'      : 'Cristina Quintero',
    'start_date' : datetime( 2014, 4, 10 ),
    'end_date'   : datetime( 9999, 12, 31 ),
    'executive'  : 0,
},
{
    'acct_id'    : 1001,
    'subdomain'  : 'touchbiztest2',
    'owner'      : 'Unknown Rep',
    'start_date' : datetime( 2014, 5, 5 ),
    'end_date'   : datetime( 9999, 12, 31 ),
    'executive'  : 0,
},
# Cust 1004 -- Sub State  Migration
{
    'acct_id'    : 1004,
    'subdomain'  : 'migrationtest',
    'owner'      : 'Cristina Quintero',
    'start_date' : datetime( 2014, 10, 10 ),
    'end_date'   : datetime( 2015, 1, 5 ),
    'executive'  : 0,
},
{
    'acct_id'    : 1004,
    'subdomain'  : 'migrationtest',
    'owner'      : 'Angela Eichner',
    'start_date' : datetime( 2015, 1, 5 ),
    'end_date'   : datetime( 9999, 12, 31 ),
    'executive'  : 0,
},
]

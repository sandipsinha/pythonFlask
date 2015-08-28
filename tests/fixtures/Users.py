"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb import Users

MODEL = Users
FIXTURES = [
{
    'acct_id'    : 1000,
    'user_id'    : 2001,
    'username'   : 'iamactor',
    'email'      : 'tom.cruise@loggly.com',
    'first_name' : 'Tom',
    'last_name'  :  'Cruise',
},
{
    'acct_id'    : 1001,
    'user_id'    : 2002,
    'username'   : 'iamsports',
    'email'      : 'carl.lewis@loggly.com',
    'first_name' : 'Carl',
    'last_name'  :  'Lewis',
},
{
    'acct_id'    : 1002,
    'user_id'    : 2003,
    'username'   : 'iamscientist',
    'email'      : 'albert.einstein@loggly.com',
    'first_name' : 'Albert',
    'last_name'  :  'Einstein',
},
{
    'acct_id'    : 1002,
    'user_id'    : 2005,
    'username'   : 'iamscientist1',
    'email'      : 'Acharya.Bose@loggly.com',
    'first_name' : 'Acharya',
    'last_name'  :  'Bose',
},
{
    'acct_id'    : 1003,
    'user_id'    : 2004,
    'username'   : 'iampolitician',
    'email'      : 'narendra.modi@loggly.com',
    'first_name' : ' ',
    'last_name'  :  ' ',
}
]

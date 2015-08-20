"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb import UserTracking

MODEL = UserTracking
FIXTURES = [
{
    'user_id'    : 2001,
    'username'   : 'iamactor',
    'session_id' : 'User11',
    'login'      :  datetime( 2014, 1, 8 ),
    'email'      : 'tom.cruise@loggly.com',
},
{
    'user_id'    : 2001,
    'username'   : 'iamactor',
    'session_id' : 'User12',
    'login'      :  datetime( 2014, 4, 5 ),
    'email'      : 'tom.cruise@loggly.com',
},
{
    'user_id'    : 2001,
    'username'   : 'iamactor',
    'session_id' : 'User13',
    'login'      :  datetime( 2014, 7, 9 ),
    'email'      : 'tom.cruise@loggly.com',
},
{
    'user_id'    : 2001,
    'username'   : 'iamactor',
    'session_id' : 'User14',
    'login'      :  datetime( 2015, 2, 9 ),
    'email'      : 'tom.cruise@loggly.com',
},
{
    'user_id'    : 2002,
    'username'   : 'iamsports',
    'session_id' : 'User21',
    'login'      :  datetime( 2014, 3, 9 ),
    'email'      : 'carl.lewis@loggly.com',
},
{
    'user_id'    : 2002,
    'username'   : 'iamsports',
     'session_id' : 'User22',
    'login'      :  datetime( 2013, 7, 9 ),
    'email'      : 'carl.lewis@loggly.com',
},
{
    'user_id'    : 2003,
    'username'   : 'iamscientist',
     'session_id' : 'User31',
    'login'      :  datetime( 2014, 7, 9 ),
    'email'      : 'albert.einstein@loggly.com',
},
{
    'user_id'    : 2003,
    'username'   : 'iamscientist',
     'session_id' : 'User32',
    'login'      :  datetime( 2015, 7, 9 ),
    'email'      : 'albert.einstein@loggly.com',
},
{
    'user_id'    : 2003,
    'username'   : 'iamscientist',
     'session_id' : 'User33',
    'login'      :  datetime( 2014, 8, 9 ),
    'email'      : 'albert.einstein@loggly.com',
},
{
    'user_id'    : 2005,
    'username'   : 'iamscientist1',
    'session_id' : 'User33',
    'login'      :  datetime( 2012, 6, 9 ),
    'email'      : 'acharya.bose@loggly.com',
}

]

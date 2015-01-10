"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from law.util.adb import Tier

MODEL = Tier
FIXTURES = [
{
    'id'   : 1,
    'name' : 'trial',
    'code' : 1,
},
{
    'id'   : 2,
    'name' : 'lite',
    'code' : 2,
},
{
    'id'   : 3,
    'name' : 'development',
    'code' : 3,
},
{
    'id'   : 4,
    'name' : 'production',
    'code' : 4,
},
{
    'id'   : 5,
    'name' : 'G1-trial',
    'code' : 100,
},
{
    'id'   : 6,
    'name' : 'G1-free',
    'code' : 200,
},
{
    'id'   : 7,
    'name' : 'G1-paid',
    'code' : 300,
},
{
    'id'   : 8,
    'name' : 'custom',
    'code' : -1,
},
]

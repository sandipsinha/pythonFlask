"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from law.util.adb_touchbiz import SalesReps

MODEL = SalesReps
FIXTURES = [
{
    'id'         : 1,
    'first'      : 'Angela',
    'last'       : 'Eichner',
    'email'      : 'angela@logglytest.com',
    'sfdc_alias' : 'aeich',
},
{
    'id'         : 2,
    'first'      : 'Stephanie',
    'last'       : 'Skuratowicz',
    'email'      : 'stephanie@logglytest.com',
    'sfdc_alias' : 'skura',
},
{
    'id'         : 3,
    'first'      : 'Michael',
    'last'       : 'Johnston',
    'email'      : 'michael@logglytest.com',
    'sfdc_alias' : 'micha',
},
{
    'id'         : 4,
    'first'      : 'Cristina',
    'last'       : 'Quintero',
    'email'      : 'cristina@logglytest.com',
    'sfdc_alias' : 'cquin',
},
]

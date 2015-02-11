"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
" CLI to kick off touchbiz processes.
"
"""
import sys
import time
import argparse
from functools import partial

from law.util.adb       import AAWSC, AAWSCOwner, loader as adb_loader, engine
from law.util.touchbiz  import TableCreator
from law.util.logger    import make_logger

LOG = make_logger( 'touchbiz-cli' )

def time_func( func ):
    start = time.time()
    func()
    end   = time.time()

    return start, end

def apply( args ):
    creator = TableCreator(
        src_table   = AAWSC,
        src_loader  = adb_loader,
        dest_table  = AAWSCOwner,
        dest_engine = engine,
    )

    localize = True if args.localize else False
    func = partial( creator.apply_ownership, localize=localize )
    start, end = time_func( func )

    LOG.info({
        'action' : 'Generate table {}'.format( creator.dest.__table__.name ),
        'elapsed': end-start,
        'status:': 'success'
    })


def cli( args ):

    commands = {
        'apply' : apply,
    }

    parser = argparse.ArgumentParser( description='Manage Touchbiz routines.' )
    subparsers = parser.add_subparsers( help='commands' )

    apply_parser = subparsers.add_parser( 'apply', help='Apply touchbiz by constructing a new table in ADB'  )
    apply_parser.set_defaults( command='apply' )
    apply_parser.add_argument( '--localize',
                               action='store_true',
                               help='Localize all DATETIME fields from UTC to US/Pacific during ownership application' )

    args = parser.parse_args( args )

    commands[args.command]( args )

    return 0

if __name__ == '__name__':
    sys.exit( cli( sys.argv[1:] ) )

"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
import unittest
from functools   import partial
from collections import namedtuple
from datetime    import datetime

from law.util import adb_touchbiz as tbz
from law.util import adb
from tests.fixtures import populate

def fixtures():
    tbz.create_touchbiz_tables()
    adb.Base.metadata.create_all( 
        bind=tbz.engine,
        tables = [
            adb.AccountState.__table__,
        ]
    )
    
    with tbz.session_context() as s:
        populate( s, model_names=['SalesReps', 'Touchbiz'] )

    with adb.session_context() as s:
        populate( s, model_names=['AccountState'] )


def setup_module():
    fixtures()

def teardown_module():
    tbz.Base.metadata.drop_all( 
        bind=tbz.engine,
        tables=[
            tbz.Touchbiz.__table__,
            tbz.SalesReps.__table__,
            tbz.SalesStages.__table__,
        ]
    )

    adb.Base.metadata.drop_all( 
        bind=tbz.engine,
        tables=[
            adb.AccountState.__table__,
        ]
    )


class TestTouchbiz( unittest.TestCase ):

    # Setup the subscription tables

    # Setup touchbiz tables

    # Setup Salesreps tables

    # Setup Sales Stages Tables

    def test_touchbiz_by_account( self ): 
        pass

    def test_touchbiz_table( self ):
        pass

    def test_add_touchbiz( self ):
        pass
    
    def test_update_touchbiz( self ):
        pass
    
    def test_sync_stages( self ):
        pass

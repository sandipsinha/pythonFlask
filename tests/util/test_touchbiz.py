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

from tests.fixtures import populate
from law.util import adb_touchbiz as tbz
from law.util import adb
from law.util import touchbiz

def fixtures():
    teardown_module()
    tbz.create_touchbiz_tables()
    adb.Base.metadata.create_all( 
        bind=tbz.engine,
        tables = [
            adb.AccountState.__table__,
            adb.Tier.__table__,
            adb.Account.__table__,
        ]
    )
    
    with tbz.session_context() as s:
        populate( s, model_names=['SalesReps', 'Touchbiz'] )

    with adb.session_context() as s:
        populate( s, model_names=['AccountState', 'Tier', 'Account'] )


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
            adb.Tier.__table__,
            adb.Account.__table__,
        ]
    )


class TestTouchbiz( unittest.TestCase ):

    # Setup the subscription tables

    # Setup touchbiz tables

    # Setup Salesreps tables

    # Setup Sales Stages Tables

    def test_apply_touchbiz( self ):

        with adb.loader() as l:
            sub_entries = l.query( adb.AccountState )\
                           .filter( adb.AccountState.acct_id == 1000 )\
                           .all()

        with tbz.loader() as l:
            company = l.query( tbz.SalesReps )\
                       .filter( tbz.SalesReps.sfdc_alias == 'integ' )\
                       .one()

            aeich = l.query( tbz.SalesReps )\
                     .filter( tbz.SalesReps.sfdc_alias == 'aeich' )\
                     .one()

            tb_entries = l.query( tbz.Touchbiz )\
                          .filter( tbz.Touchbiz.acct_id == 1000 )\
                          .all()

        applied = touchbiz.apply_touchbiz( sub_entries, tb_entries )

        self.assertEqual( len( applied ), 4 )
        self.assertEqual( applied[0].owner.sfdc_alias, company.sfdc_alias )
        self.assertEqual( applied[1].owner.sfdc_alias, company.sfdc_alias )
        self.assertEqual( applied[2].owner.sfdc_alias, aeich.sfdc_alias )
        self.assertEqual( applied[3].owner.sfdc_alias, aeich.sfdc_alias )

    def test_touchbiz_by_account_id( self ): 
        with tbz.loader() as l:
            company = l.query( tbz.SalesReps )\
                       .filter( tbz.SalesReps.sfdc_alias == 'integ' )\
                       .one()

            aeich = l.query( tbz.SalesReps )\
                     .filter( tbz.SalesReps.sfdc_alias == 'aeich' )\
                     .one()


        rows = touchbiz.touchbiz_by_account_id( 1000 )

        self.assertEqual( len( rows ), 4 )
        self.assertEqual( rows[0].owner.sfdc_alias, company.sfdc_alias )
        self.assertEqual( rows[1].owner.sfdc_alias, company.sfdc_alias )
        self.assertEqual( rows[2].owner.sfdc_alias, aeich.sfdc_alias )
        self.assertEqual( rows[3].owner.sfdc_alias, aeich.sfdc_alias )

    def test_touchbiz_by_account( self ): 
        with tbz.loader() as l:
            company = l.query( tbz.SalesReps )\
                       .filter( tbz.SalesReps.sfdc_alias == 'integ' )\
                       .one()

            aeich = l.query( tbz.SalesReps )\
                     .filter( tbz.SalesReps.sfdc_alias == 'aeich' )\
                     .one()


        rows = touchbiz.touchbiz_by_account('touchbiztest')

        self.assertEqual( len( rows ), 4 )
        self.assertEqual( rows[0].owner.sfdc_alias, company.sfdc_alias )
        self.assertEqual( rows[1].owner.sfdc_alias, company.sfdc_alias )
        self.assertEqual( rows[2].owner.sfdc_alias, aeich.sfdc_alias )
        self.assertEqual( rows[3].owner.sfdc_alias, aeich.sfdc_alias )

    def test_touchbiz_table( self ):
        pass

    def test_add_touchbiz( self ):
        pass
    
    def test_update_touchbiz( self ):
        pass
    
    def test_sync_stages( self ):
        pass

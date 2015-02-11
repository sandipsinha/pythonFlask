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
from law.util import touchbizdb as tbz
from law.util import adb
from law.util import touchbiz
from law.util import touchbiz_cli

def fixtures():
    teardown_module()
    tbz.create_touchbiz_tables()
    adb.Base.metadata.create_all( 
        bind=tbz.engine,
        tables = [
            adb.AccountStateUncompressed.__table__,
            adb.AAWSC.__table__,
            adb.Tier.__table__,
            adb.Account.__table__,
            adb.AccountActivity.__table__,
            adb.AAOwner.__table__,
        ]
    )
    
    with tbz.session_context() as s:
        populate( s, model_names=['SalesReps', 'Touchbiz'] )

    with adb.session_context() as s:
        populate( s, model_names=[
                        'AccountStateUncompressed', 
                        'AAWSC',
                        'Tier', 
                        'Account', 
                        'AccountActivity']
        )


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
            adb.AccountStateUncompressed.__table__,
            adb.AAWSC.__table__,
            adb.Tier.__table__,
            adb.Account.__table__,
            adb.AccountActivity.__table__,
            adb.AAOwner.__table__,
        ]
    )


class TestTouchbiz( unittest.TestCase ):

    def test_apply_touchbiz( self ):

        with adb.loader() as l:
            sub_entries = l.query( adb.AccountStateUncompressed )\
                           .filter( adb.AccountStateUncompressed.acct_id == 1000 )\
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
        self.assertEqual( applied[0].status, 'won' )
        self.assertEqual( applied[1].owner.sfdc_alias, company.sfdc_alias )
        self.assertEqual( applied[0].status, 'won' )
        self.assertEqual( applied[2].owner.sfdc_alias, aeich.sfdc_alias )
        self.assertEqual( applied[0].status, 'won' )
        self.assertEqual( applied[3].owner.sfdc_alias, aeich.sfdc_alias )
        self.assertEqual( applied[0].status, 'won' )

        with adb.loader() as l:
            sub_entries = l.query( adb.AccountStateUncompressed )\
                           .filter( adb.AccountStateUncompressed.acct_id == 1001 )\
                           .all()

        with tbz.loader() as l:
            company = l.query( tbz.SalesReps )\
                       .filter( tbz.SalesReps.sfdc_alias == 'integ' )\
                       .one()

            aeich = l.query( tbz.SalesReps )\
                     .filter( tbz.SalesReps.sfdc_alias == 'aeich' )\
                     .one()
            
            skura = l.query( tbz.SalesReps )\
                     .filter( tbz.SalesReps.sfdc_alias == 'skura' )\
                     .one()

            tb_entries = l.query( tbz.Touchbiz )\
                          .filter( tbz.Touchbiz.acct_id == 1001 )\
                          .all()

        
        applied = touchbiz.apply_touchbiz( sub_entries, tb_entries )

        self.assertEqual( len( applied ), 4 )
        self.assertEqual( applied[0].owner.sfdc_alias, company.sfdc_alias )
        self.assertEqual( applied[0].status, 'won' )
        self.assertEqual( applied[1].owner.sfdc_alias, skura.sfdc_alias )
        self.assertEqual( applied[1].status, 'won' )
        self.assertEqual( applied[2].owner.sfdc_alias, skura.sfdc_alias )
        self.assertEqual( applied[2].status, 'won' )
        self.assertEqual( applied[3].owner.sfdc_alias, skura.sfdc_alias )
        self.assertEqual( applied[3].status, 'pending' )

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
    
    def test_tuplify( self ):
        with tbz.loader() as l:
            company = l.query( tbz.SalesReps )\
                       .filter( tbz.SalesReps.sfdc_alias == 'integ' )\
                       .one()

            aeich = l.query( tbz.SalesReps )\
                     .filter( tbz.SalesReps.sfdc_alias == 'aeich' )\
                     .one()


        columns = ('tRate', 'tGB', 'tDays', 'owner.sfdc_alias', 'owner.email' )
        rows = touchbiz.tuplify( touchbiz.touchbiz_by_account_id(1000), columns )

        self.assertEqual( len( rows ), 4 )
        self.assertEqual( rows[0][0], ( 'tRate', 0 ) )
        self.assertEqual( rows[0][1], ( 'tGB', 0 ) )
        self.assertEqual( rows[0][2], ( 'tDays', 15 ) )
        self.assertEqual( rows[0][3], ( 'owner.sfdc_alias', company.sfdc_alias ) )
        self.assertEqual( rows[0][4], ( 'owner.email', company.email ) )
       
        self.assertEqual( rows[1][0], ( 'tRate', 0 ) )
        self.assertEqual( rows[1][1], ( 'tGB', 200000000 ) )
        self.assertEqual( rows[1][2], ( 'tDays', 7 ) )
        self.assertEqual( rows[1][3], ( 'owner.sfdc_alias', company.sfdc_alias ) )
        self.assertEqual( rows[1][4], ( 'owner.email', company.email ) )
        
        self.assertEqual( rows[2][0], ( 'tRate', 49 ) )
        self.assertEqual( rows[2][1], ( 'tGB', 1000000000 ) )
        self.assertEqual( rows[2][2], ( 'tDays', 7 ) )
        self.assertEqual( rows[2][3], ( 'owner.sfdc_alias', aeich.sfdc_alias ) )
        self.assertEqual( rows[2][4], ( 'owner.email', aeich.email ) )
        
        self.assertEqual( rows[3][0], ( 'tRate', 99 ) )
        self.assertEqual( rows[3][1], ( 'tGB', 2000000000 ) )
        self.assertEqual( rows[3][2], ( 'tDays', 15 ) )
        self.assertEqual( rows[3][3], ( 'owner.sfdc_alias', aeich.sfdc_alias ) )
        self.assertEqual( rows[3][4], ( 'owner.email', aeich.email ) )
    
    def test_dictify( self ):
        with tbz.loader() as l:
            company = l.query( tbz.SalesReps )\
                       .filter( tbz.SalesReps.sfdc_alias == 'integ' )\
                       .one()

            aeich = l.query( tbz.SalesReps )\
                     .filter( tbz.SalesReps.sfdc_alias == 'aeich' )\
                     .one()


        columns = ('tRate', 'tGB', 'tDays', 'owner.sfdc_alias', 'owner.email' )
        rows = touchbiz.dictify( touchbiz.touchbiz_by_account_id(1000), columns )

        self.assertEqual( len( rows ), 4 )
        self.assertEqual( rows[0][ 'tRate' ], 0 )
        self.assertEqual( rows[0][ 'tGB' ], 0 )
        self.assertEqual( rows[0][ 'tDays' ], 15 )
        self.assertEqual( rows[0][ 'owner.sfdc_alias' ], company.sfdc_alias )
        self.assertEqual( rows[0][ 'owner.email' ], company.email )
       
        self.assertEqual( rows[1][ 'tRate' ], 0 )
        self.assertEqual( rows[1][ 'tGB' ], 200000000 )
        self.assertEqual( rows[1][ 'tDays' ], 7 )
        self.assertEqual( rows[1][ 'owner.sfdc_alias' ], company.sfdc_alias )
        self.assertEqual( rows[1][ 'owner.email' ], company.email )
        
        self.assertEqual( rows[2][ 'tRate' ], 49 )
        self.assertEqual( rows[2][ 'tGB' ], 1000000000 )
        self.assertEqual( rows[2][ 'tDays' ], 7 )
        self.assertEqual( rows[2][ 'owner.sfdc_alias' ], aeich.sfdc_alias )
        self.assertEqual( rows[2][ 'owner.email' ], aeich.email )
        
        self.assertEqual( rows[3][ 'tRate' ], 99 )
        self.assertEqual( rows[3][ 'tGB' ], 2000000000 )
        self.assertEqual( rows[3][ 'tDays' ], 15 )
        self.assertEqual( rows[3][ 'owner.sfdc_alias' ], aeich.sfdc_alias )
        self.assertEqual( rows[3][ 'owner.email' ], aeich.email )
    
    def test_flatten( self ):
        with tbz.loader() as l:
            company = l.query( tbz.SalesReps )\
                       .filter( tbz.SalesReps.sfdc_alias == 'integ' )\
                       .one()

            aeich = l.query( tbz.SalesReps )\
                     .filter( tbz.SalesReps.sfdc_alias == 'aeich' )\
                     .one()


        rows = touchbiz.touchbiz_by_account_id(1002)

        row = touchbiz.flatten( rows[0] )
        self.assertEqual( row.created, datetime( 2014, 4, 8) )
        self.assertEqual( row.tier, 'trial' )
        self.assertEqual( row.retention, 15 )
        self.assertEqual( row.volume, 0 )
        self.assertEqual( row.rate, 0 )
        self.assertEqual( row.owner, company.sfdc_alias )

        row = touchbiz.flatten( rows[1] )
        self.assertEqual( row.created, datetime( 2014, 9, 22, 1) )
        self.assertEqual( row.tier, 'development' )
        self.assertEqual( row.retention, 7 )
        self.assertEqual( row.volume, 1000000000 )
        self.assertEqual( row.rate, 49 )
        self.assertEqual( row.owner, company.sfdc_alias )

        row = touchbiz.flatten( rows[2] )
        self.assertEqual( row.created, 'pending' )
        self.assertEqual( row.tier, 'Production' )
        self.assertEqual( row.retention, 15 )
        self.assertEqual( row.volume, '200000000000' )
        self.assertEqual( row.rate, 109 )
        self.assertEqual( row.owner, aeich.sfdc_alias )

    def test_aaowners( self ):
        creator = touchbiz.AAOwnerCreator()
        creator.apply_ownership()

        with adb.loader() as l:
            source = l.query( adb.AccountActivity )\
                      .order_by( adb.AccountActivity.acct_id, adb.AccountActivity.updated )\
                      .all()
            owners = l.query( adb.AAOwner )\
                      .order_by( adb.AAOwner.acct_id, adb.AAOwner.updated )\
                      .all()

        columns = [ 
            'acct_id',
            'created',
            'updated',
            'from_vol_bytes',
            'from_ret_days',
            'from_sub_rate',
            'from_plan_id',
            'from_sched_id',
            'from_bill_per',
            'from_bill_chan',
            'to_vol_bytes',
            'to_ret_days',
            'to_sub_rate',
            'to_plan_id',
            'to_sched_id',
            'to_bill_per',
            'to_bill_chan',
            'trial_exp',
        ]

        # Make sure that every column except the 'owner' col is the exact same
        # in the dest table (AAOwner) as the source table (account activity)
        for i in xrange( len( source ) ):
            for col in columns:
                self.assertEqual( getattr( source[i], col ), getattr( owners[i], col ) )

        self.assertEqual( len( owners ), 10 )

        self.assertEqual( owners[0].owner, 'Hoover Loggly' )
        self.assertEqual( owners[1].owner, 'Hoover Loggly' )
        self.assertEqual( owners[2].owner, 'Angela Eichner' )
        self.assertEqual( owners[3].owner, 'Angela Eichner' )

        self.assertEqual( owners[4].owner, 'Hoover Loggly' )
        self.assertEqual( owners[5].owner, 'Stephanie Skuratowicz' )
        self.assertEqual( owners[6].owner, 'Stephanie Skuratowicz' )
        
        self.assertEqual( owners[7].owner, 'Hoover Loggly' )
        self.assertEqual( owners[8].owner, 'Hoover Loggly' )

    def test_add_touchbiz( self ):
        pass
    
    def test_update_touchbiz( self ):
        pass
    
    def test_sync_stages( self ):
        pass


class TestTouchbizCLI( unittest.TestCase ):

    @classmethod
    def setup_class( cls ):
        adb.Base.metadata.create_all( 
            bind=tbz.engine,
            tables = [
                adb.AAWSCOwner.__table__,
            ]
        )

    @classmethod
    def teardown_class( cls ):
        adb.Base.metadata.drop_all( 
            bind=tbz.engine,
            tables=[
                adb.AAWSCOwner.__table__,
            ]
        )

    def test_apply( self ):
        touchbiz_cli.cli( ['apply'] )

        with adb.loader() as l:
            rows = l.query( adb.AAWSCOwner ).all()

        self.assertTrue( len( rows ) > 0 )
        for row in rows:
            self.assertIsNotNone( row.owner )

        touchbiz_cli.cli( ['apply', '--localize'] )

        with adb.loader() as l:
            rows = l.query( adb.AAWSCOwner ).all()

        self.assertTrue( len( rows ) > 0 )
        for row in rows:
            self.assertIsNotNone( row.owner )

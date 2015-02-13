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
from law.util.touchbiz_gifts import DataSource, DataDestination, AccountOwnersMigrator

def fixtures():
    # In case the test DB was in a bad state
    teardown_module()

    adb.Base.metadata.create_all( 
        bind=tbz.engine,
        tables = [
            adb.Owners.__table__,
        ]
    )
    
    with adb.session_context() as s:
        populate( s, model_names=['Owners'] )

    tbz.Base.metadata.create_all( 
        bind=tbz.engine,
        tables=[
            tbz.SalesReps.__table__,
            tbz.Touchbiz.__table__,
        ]
    )

    with tbz.session_context() as s:
        populate( s, model_names=['SalesReps'] )


def setup_module():
    fixtures()

def teardown_module():
    adb.Base.metadata.drop_all( 
        bind=tbz.engine,
        tables=[
            adb.Owners.__table__,
        ]
    )

    tbz.Base.metadata.drop_all( 
        bind=tbz.engine,
        tables=[
            tbz.SalesReps.__table__,
            tbz.Touchbiz.__table__,
        ]
    )


class TestTouchbizGifts( unittest.TestCase ):

    def test_migrate_columns( self ):
        src   = DataSource( adb.Owners, adb.loader )
        dest  = DataDestination( tbz.Touchbiz, tbz.engine )

        with src.loader() as l:
            owners = l.query( src.table ).order_by( src.table.owner ).all()

        migrator = AccountOwnersMigrator( src, dest )

        migrated = migrator.migrate_columns( owners[0] ) 
        self.assertEqual( migrated['acct_id'],        1000 )
        self.assertEqual( migrated['sales_rep_id'],   2 )
        self.assertEqual( migrated['created'],        datetime( 2014, 4, 8, 7) )
        self.assertEqual( migrated['modified'],       datetime( 2014, 4, 8, 7 ) )
        self.assertEqual( migrated['tier'],           '' )
        self.assertEqual( migrated['retention'],      0 )
        self.assertEqual( migrated['volume'],         0 )
        self.assertEqual( migrated['sub_rate'],       0 )
        self.assertEqual( migrated['billing_period'], '' )

        migrated = migrator.migrate_columns( owners[1] ) 
        self.assertEqual( migrated['acct_id'],        1000 )
        self.assertEqual( migrated['sales_rep_id'],   5 )
        self.assertEqual( migrated['created'],        datetime( 2014, 4, 10, 7 ) )
        self.assertEqual( migrated['modified'],       datetime( 2014, 4, 10, 7 ) )
        self.assertEqual( migrated['tier'],           '' )
        self.assertEqual( migrated['retention'],      0 )
        self.assertEqual( migrated['volume'],         0 )
        self.assertEqual( migrated['sub_rate'],       0 )
        self.assertEqual( migrated['billing_period'], '' )

        # No default rep
        with self.assertRaises( KeyError ):
            migrated = migrator.migrate_columns( owners[2] ) 


    def test_migrate( self ):
        src   = DataSource( adb.Owners, adb.loader )
        dest  = DataDestination( tbz.Touchbiz, tbz.engine )

        migrator = AccountOwnersMigrator( src, dest, default_rep='Hoover Loggly' )
        migrator.migrate()

        with tbz.loader() as l:
            touchbiz = l.query( tbz.Touchbiz ).all()

        self.assertEqual( len( touchbiz ), 3 )

        entry = touchbiz[0]
        self.assertEqual( entry.acct_id,        1000 )
        self.assertEqual( entry.sales_rep_id,   2 )
        self.assertEqual( entry.created,        datetime( 2014, 4, 8, 7 ) )
        self.assertEqual( entry.modified,       datetime( 2014, 4, 8, 7 ) )
        self.assertEqual( entry.tier,           '' )
        self.assertEqual( entry.retention,      0 )
        self.assertEqual( entry.volume,         '0' )
        self.assertEqual( entry.sub_rate,       0 )
        self.assertEqual( entry.billing_period, '' )

        entry = touchbiz[1]
        self.assertEqual( entry.acct_id,        1000 )
        self.assertEqual( entry.sales_rep_id,   5 )
        self.assertEqual( entry.created,        datetime( 2014, 4, 10, 7 ) )
        self.assertEqual( entry.modified,       datetime( 2014, 4, 10, 7 ) )
        self.assertEqual( entry.tier,           '' )
        self.assertEqual( entry.retention,      0 )
        self.assertEqual( entry.volume,         '0' )
        self.assertEqual( entry.sub_rate,       0 )
        self.assertEqual( entry.billing_period, '' )
        
        entry = touchbiz[2]
        self.assertEqual( entry.acct_id,        1001 )
        self.assertEqual( entry.sales_rep_id,   1 )
        self.assertEqual( entry.created,        datetime( 2014, 5, 5, 7 ) )
        self.assertEqual( entry.modified,       datetime( 2014, 5, 5, 7 ) )
        self.assertEqual( entry.tier,           '' )
        self.assertEqual( entry.retention,      0 )
        self.assertEqual( entry.volume,         '0' )
        self.assertEqual( entry.sub_rate,       0 )
        self.assertEqual( entry.billing_period, '' )

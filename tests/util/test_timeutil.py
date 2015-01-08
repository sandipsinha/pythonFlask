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

from law.util.timeutil import Timebucket, BucketedList, iso8601_to_dt

DatedItem = namedtuple( 'DatedItem', ['value', 'created'] )

class TestBucketedList( unittest.TestCase ):

    def test_construction( self ):
        bl = BucketedList()
        self.assertEqual( isinstance( bl, (dict, BucketedList) ), True )
        
        bl['2014'] = [1,2,3]
        bl['2013'] = [4,5,6]

        self.assertEqual( bl['2014'], [1,2,3] )
        self.assertEqual( bl['2013'], [4,5,6] )

    def test_periods( self ):
        bl = BucketedList({
            '2014' : [1,2,3],
            '2013' : [4,5,6],
        })

        self.assertEqual( bl.periods, bl.keys() )
        self.assertEqual( bl.periods, ['2014', '2013'] )

    def test_get_period_set( self ):
        bl1 = BucketedList( {'2014':[1,2], '2013':[3,4], '1999':[5,6]} )
        bl2 = BucketedList( {'2014':[1,2], '2013':[3,4], '2011':[5,6]} )
        pset = BucketedList.period_set( bl1, bl2 )

        self.assertEqual( pset, set(( '2014', '2013', '2011', '1999' )) )

    def test_period_map( self ):
        bl1 = BucketedList( {'2014':[1,2], '2013':[3,4], '1999':[5,6]} )
        bl1.period_map( sum )

        self.assertEqual( bl1['2014'], 3 )
        self.assertEqual( bl1['2013'], 7 )
        self.assertEqual( bl1['1999'], 11 )
        
        bl1 = BucketedList( {'2014':[1,2], '2013':[3,4], '1999':[5,6]} )
        bl1.period_map( partial( map, lambda x: x+1 ) )
        self.assertEqual( bl1['2014'], [2,3] )
        self.assertEqual( bl1['2013'], [4,5] )
        self.assertEqual( bl1['1999'], [6,7] )

    def test_extend( self ):
        bl1 = BucketedList( {'2014':[1,2], '2013':[3,4], '1999':[5,6]} )
        bl2 = BucketedList( {'2014':[1,2], '2013':[3,4], '2011':[5,6]} )

        bl1.extend( bl2 )

        self.assertEqual( bl1, {
            '2014':[1,2,1,2],
            '2013':[3,4,3,4],
            '2011':[5,6],
            '1999':[5,6],
        })

    def test_fill_empty_periods( self ):
        bl1 = BucketedList( {'2014':[1,2], '2013':[3,4], '1999':[5,6]} )
        bl2 = BucketedList( {'2014':[1,2], '2013':[3,4], '2011':[5,6]} )
        pset = BucketedList.period_set( bl1, bl2 )

        bl1.fill_missing_periods( pset )
        self.assertEqual( set( bl1.periods ), set(( '2014', '2013', '2011', '1999' )) )
        self.assertEqual( bl1['2014'], [ 1, 2 ] )
        self.assertEqual( bl1['2013'], [ 3, 4 ] )
        self.assertEqual( bl1['2011'], [] )
        self.assertEqual( bl1['1999'], [ 5, 6 ] )

        
        bl2.fill_missing_periods( pset, 0 )
        self.assertEqual( set( bl2.periods ), set(( '2014', '2013', '2011', '1999' )) )
        self.assertEqual( bl2['2014'], [ 1, 2 ] )
        self.assertEqual( bl2['2013'], [ 3, 4 ] )
        self.assertEqual( bl2['2011'], [ 5, 6 ] )
        self.assertEqual( bl2['1999'], 0 )


class TestTimebucket( unittest.TestCase ):

    def test_properties( self ):
        rows = [
            DatedItem( 2, datetime(2014, 6, 9) ),
            DatedItem( 1, datetime(2010, 2, 12) ),
            DatedItem( 3, datetime(2011, 8, 10) ),
            DatedItem( 4, datetime(2014, 12, 31) ),
        ]
        
        bucketer = Timebucket( rows, 'created' )
        self.assertEqual( bucketer.start, datetime( 2010, 2, 12 ) )
        self.assertEqual( bucketer.end,   datetime( 2014, 12, 31 ) )
        self.assertEqual( bucketer.rows, [
            DatedItem( 1, datetime(2010, 2, 12) ),
            DatedItem( 3, datetime(2011, 8, 10) ),
            DatedItem( 2, datetime(2014, 6, 9) ),
            DatedItem( 4, datetime(2014, 12, 31) )
        ])
    def test_year( self ):
        rows = [
            DatedItem( 2, datetime(2014, 6, 9) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        yearly = bucketer.year()

        self.assertEqual( yearly['2014'], [ DatedItem( 2, datetime( 2014, 6, 9 ) ) ] )
        
        rows = [
            DatedItem( 2, datetime(2014, 6, 9) ),
            DatedItem( 3, datetime(2014, 12, 31) ),
            DatedItem( 1, datetime(2014, 1, 1) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        yearly = bucketer.year()

        self.assertEqual( 
            yearly['2014'], 
            [ 
              DatedItem( 1, datetime( 2014, 1, 1 ) ),
              DatedItem( 2, datetime( 2014, 6, 9 ) ),
              DatedItem( 3, datetime( 2014, 12, 31 ) )
            ]
        )

        rows = [
            DatedItem( 1, datetime(2010, 6, 9) ),
            DatedItem( 4, datetime(2014, 12, 31) ),
            DatedItem( 2, datetime(2012, 12, 31) ),
            DatedItem( 3, datetime(2014, 1, 1) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        yearly = bucketer.year()

        self.assertEqual( yearly['2010'], [ DatedItem( 1, datetime( 2010, 6, 9 ) )] )
        self.assertEqual( yearly['2011'], [] )
        self.assertEqual( yearly['2012'], [ DatedItem( 2, datetime( 2012, 12, 31 ) )] )
        self.assertEqual( yearly['2013'], [] )
        self.assertEqual( yearly['2014'], [ DatedItem( 3, datetime( 2014, 1, 1 ) ), 
                                            DatedItem( 4, datetime( 2014, 12, 31 ) ), 
                                        ] )

    def test_quarter( self ):
        rows = [
            DatedItem( 2, datetime(2014, 6, 9) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        quartered = bucketer.quarter()

        self.assertEqual( quartered['2014-Q1'], [] )
        self.assertEqual( quartered['2014-Q2'], [ DatedItem( 2, datetime( 2014, 6, 9 ) ) ] )
        self.assertEqual( quartered['2014-Q3'], [] )
        self.assertEqual( quartered['2014-Q4'], [] )

        rows = [
            DatedItem( 1, datetime(2014, 2, 12) ),
            DatedItem( 2, datetime(2014, 6, 9) ),
            DatedItem( 3, datetime(2014, 8, 10) ),
            DatedItem( 4, datetime(2014, 12, 31, 23, 59, 59) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        quartered = bucketer.quarter()

        self.assertEqual( quartered['2014-Q1'], [ DatedItem( 1, datetime( 2014, 2, 12 ) ) ] )
        self.assertEqual( quartered['2014-Q2'], [ DatedItem( 2, datetime( 2014, 6, 9 ) ) ] )
        self.assertEqual( quartered['2014-Q3'], [ DatedItem( 3, datetime( 2014, 8, 10 ) ) ] )
        self.assertEqual( quartered['2014-Q4'], [ DatedItem( 4, datetime( 2014, 12, 31, 23, 59, 59 ) ) ] )

        rows = [
            DatedItem( 1, datetime(2010, 8, 12) ),
            DatedItem( 2, datetime(2012, 1, 1) ),
            DatedItem( 3, datetime(2012, 3, 31) ),
            DatedItem( 4, datetime(2014, 12, 31) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        quartered = bucketer.quarter()

        self.assertEqual( quartered['2010-Q1'], [] )
        self.assertEqual( quartered['2010-Q2'], [] )
        self.assertEqual( quartered['2010-Q3'], [ DatedItem( 1, datetime( 2010, 8, 12 ) ) ] )
        self.assertEqual( quartered['2010-Q4'], [] )
        self.assertEqual( quartered['2011-Q1'], [] )
        self.assertEqual( quartered['2011-Q2'], [] )
        self.assertEqual( quartered['2011-Q3'], [] )
        self.assertEqual( quartered['2011-Q4'], [] )
        self.assertEqual( quartered['2012-Q1'], [ DatedItem( 2, datetime( 2012, 1, 1 ) ), 
                                                  DatedItem( 3, datetime( 2012, 3, 31 ) ) ] 
                        )
        self.assertEqual( quartered['2012-Q2'], [] )
        self.assertEqual( quartered['2012-Q3'], [] )
        self.assertEqual( quartered['2012-Q4'], [] )
        self.assertEqual( quartered['2013-Q1'], [] )
        self.assertEqual( quartered['2013-Q2'], [] )
        self.assertEqual( quartered['2013-Q3'], [] )
        self.assertEqual( quartered['2013-Q4'], [] )
        self.assertEqual( quartered['2014-Q1'], [] )
        self.assertEqual( quartered['2014-Q2'], [] )
        self.assertEqual( quartered['2014-Q3'], [] )
        self.assertEqual( quartered['2014-Q4'], [ DatedItem( 4, datetime( 2014, 12, 31 ) ) ] )


    def test_month( self ):
        rows = [
            DatedItem( 2, datetime(2014, 6, 9) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        monthed = bucketer.month()

        self.assertEqual( monthed['2014-06'], [ DatedItem( 2, datetime( 2014, 6, 9 ) ) ] )
        
        rows = [
            DatedItem( 2, datetime(2014, 6, 9) ),
            DatedItem( 2, datetime(2014, 2, 28) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        monthed = bucketer.month()

        self.assertEqual( monthed['2014-02'], [ DatedItem( 2, datetime( 2014, 2, 28 ) ) ] )
        self.assertEqual( monthed['2014-03'], [] )
        self.assertEqual( monthed['2014-04'], [] )
        self.assertEqual( monthed['2014-05'], [] )
        self.assertEqual( monthed['2014-06'], [ DatedItem( 2, datetime( 2014, 6, 9 ) ) ] )
        
        rows = [
            DatedItem( 1, datetime(2013, 1, 1) ),
            DatedItem( 2, datetime(2014, 2, 28) ),
            DatedItem( 3, datetime(2014, 2, 10) ),
            DatedItem( 4, datetime(2014, 12, 31, 23, 59, 59) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        monthed = bucketer.month()

        self.assertEqual( monthed['2013-01'], [ DatedItem( 1, datetime( 2013, 1, 1 ) ) ] )
        self.assertEqual( monthed['2013-02'], [] )
        self.assertEqual( monthed['2013-03'], [] )
        self.assertEqual( monthed['2013-04'], [] )
        self.assertEqual( monthed['2013-05'], [] )
        self.assertEqual( monthed['2013-06'], [] )
        self.assertEqual( monthed['2013-07'], [] )
        self.assertEqual( monthed['2013-08'], [] )
        self.assertEqual( monthed['2013-09'], [] )
        self.assertEqual( monthed['2013-10'], [] )
        self.assertEqual( monthed['2013-11'], [] )
        self.assertEqual( monthed['2013-12'], [] )
        self.assertEqual( monthed['2014-02'], [ DatedItem( 3, datetime( 2014, 2, 10 ) ), DatedItem( 2, datetime( 2014, 2, 28 ) )  ] )
        self.assertEqual( monthed['2014-03'], [] )
        self.assertEqual( monthed['2014-04'], [] )
        self.assertEqual( monthed['2014-05'], [] )
        self.assertEqual( monthed['2014-06'], [] )
        self.assertEqual( monthed['2014-07'], [] )
        self.assertEqual( monthed['2014-08'], [] )
        self.assertEqual( monthed['2014-09'], [] )
        self.assertEqual( monthed['2014-10'], [] )
        self.assertEqual( monthed['2014-11'], [] )
        self.assertEqual( monthed['2014-12'], [ DatedItem( 4, datetime( 2014, 12, 31, 23, 59, 59 ) ) ] )

    def test_week( self ):
        rows = [
            DatedItem( 2, datetime(2014, 6, 9) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        week = bucketer.week()
        
        self.assertEqual( week['2014-W24'], [ DatedItem( 2, datetime( 2014, 6, 9 ) ) ] )


    def test_day( self ):
        pass

class TestISO8601( unittest.TestCase ):

    def test_iso8601_to_dt( self ):
        self.assertEqual( iso8601_to_dt( '2014-04-08' ),          datetime( 2014, 4, 8 ) )
        self.assertEqual( iso8601_to_dt( '2014-04-08T01' ),       datetime( 2014, 4, 8, 1 ) )
        self.assertEqual( iso8601_to_dt( '2014-04-08T01:02' ),    datetime( 2014, 4, 8, 1, 2 ) )
        self.assertEqual( iso8601_to_dt( '2014-04-08T01:02:03' ), datetime( 2014, 4, 8, 1, 2, 3 ) )



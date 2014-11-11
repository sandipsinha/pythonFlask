"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
import unittest
from collections import namedtuple
from datetime    import datetime

from law.util.timeutil import Timebucket

DatedItem = namedtuple( 'DatedItem', ['value', 'created'] )

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
            DatedItem( 4, datetime(2014, 12, 31) ),
        ]
        bucketer  = Timebucket( rows, 'created' )
        quartered = bucketer.quarter()

        self.assertEqual( quartered['2014-Q1'], [ DatedItem( 1, datetime( 2014, 2, 12 ) ) ] )
        self.assertEqual( quartered['2014-Q2'], [ DatedItem( 2, datetime( 2014, 6, 9 ) ) ] )
        self.assertEqual( quartered['2014-Q3'], [ DatedItem( 3, datetime( 2014, 8, 10 ) ) ] )
        self.assertEqual( quartered['2014-Q4'], [ DatedItem( 4, datetime( 2014, 12, 31 ) ) ] )

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
            DatedItem( 4, datetime(2014, 12, 31) ),
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
        self.assertEqual( monthed['2014-12'], [ DatedItem( 4, datetime( 2014, 12, 31 ) ) ] )

    def test_week( self ):
        pass

    def test_day( self ):
        pass

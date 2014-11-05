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
        pass

    def test_quarter( self ):
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


    def test_month( self ):
        pass

    def test_week( self ):
        pass

    def test_day( self ):
        pass

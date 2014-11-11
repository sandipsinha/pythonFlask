"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
import calendar
from operator    import attrgetter
from collections import defaultdict
from datetime    import datetime, timedelta


class Timebucket( object ):
    """ Performs datetime based segmentation of the dataset """

    _QUARTER = {
        'Q1' : { 'start':(1,1),  'end':(3,31)  },
        'Q2' : { 'start':(4,1),  'end':(6,30)  },
        'Q3' : { 'start':(7,1),  'end':(9,30)  },
        'Q4' : { 'start':(10,1), 'end':(12,31) },
    }

    def __init__( self, rows, key ):
        """ Assumes that key is the accessor name of the datetime object for
        each row """

        self._getter = attrgetter( key )
        self.rows    = sorted( rows, key=self._getter )
        self.key     = key

    @property 
    def start(self):
        return self._getter( self.rows[0] )
    
    @property 
    def end(self):
        return self._getter( self.rows[-1] )

    def year( self ):
        segmented     = {}
        segment_start = 0

        for year in range( self.start.year, self.end.year + 1):
            start_date = datetime( year, 1, 1 ) if year != self.start.year else datetime( *self.start.timetuple()[:3] )
            end_date   = datetime( year, 12, 31 ) if year != self.end.year else datetime( *self.end.timetuple()[:3] )
            sname      = str(year)

            segmented[sname] = []

            for i, row in enumerate( self.rows[segment_start:], segment_start ):
                if self._getter( row ) >= start_date and self._getter(row) <= end_date:
                    segmented[sname].append( row )
                elif self._getter( row ) > end_date:
                    segment_start = i
                    break

        return segmented

    def quarter( self ):
        """ Returns a dictionary of items that are grouped by Year-Quarter key names. """
        segmented     = {}
        segment_start = 0

        for year in range( self.start.year, self.end.year + 1):
            for quarter in ('Q1', 'Q2', 'Q3', 'Q4'):
                start_date = datetime( year, *self._QUARTER[quarter]['start'] )
                end_date   = datetime( year, *self._QUARTER[quarter]['end'] )
                sname      = '{}-{}'.format( year, quarter )

                segmented[sname] = []

                for i, row in enumerate( self.rows[segment_start:], segment_start ):
                    if self._getter( row ) >= start_date and self._getter(row) <= end_date:
                        segmented[sname].append( row )
                    elif self._getter( row ) > end_date:
                        segment_start = i
                        break

        return segmented
    
    def month( self ):
        """ Returns a dictionary of items that are grouped by date (to month granularity)
        key names. 
        """
        segmented     = {}
        segment_start = 0

        for year in range( self.start.year, self.end.year + 1):
            start_month = datetime( year, 1, 1 ) if year != self.start.year else datetime( *self.start.timetuple()[:3] )
            end_month   = datetime( year, 12, 31 ) if year != self.end.year else datetime( *self.end.timetuple()[:3] )

            for month in range( start_month.month, end_month.month + 1 ):
                start_date = datetime( year, month, 1 )
                end_date   = datetime( year, month, calendar.monthrange( year, month )[-1] )
                sname      = start_date.strftime( '%Y-%m' )

                segmented[ sname ] = []

                for i, row in enumerate( self.rows[segment_start:], segment_start ):
                    if self._getter( row ) >= start_date and self._getter(row) <= end_date:
                        segmented[ sname ].append( row )
                    elif self._getter( row ) > end_date:
                        segment_start = i
                        break

        return segmented
    
    def week( self ):
        pass
    
    def day( self ):
        pass

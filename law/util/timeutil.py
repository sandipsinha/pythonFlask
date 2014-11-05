"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from operator import attrgetter
from datetime import datetime


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
        self.rows   = sorted( rows, key=self._getter )
        self.key    = key

    @property 
    def start(self):
        return self._getter( self.rows[0] )
    
    @property 
    def end(self):
        return self._getter( self.rows[-1] )

    def year( self ):
        pass

    def quarter( self ):
        years         = self.end.year - self.start.year
        segmented     = {}
        num_rows      = len( self.rows )
        segment_start = 0
        segment_end   = 0

        for year in range( self.start.year, self.end.year + 1):
            for quarter in ('Q1', 'Q2', 'Q3', 'Q4'):
                start_date = datetime( year, *self._QUARTER[quarter]['start'] )
                end_date   = datetime( year, *self._QUARTER[quarter]['end'] )

                sname      = '{}-{}'.format( year, quarter )

                for i, row in enumerate( self.rows[segment_start:] ):
                    if self._getter( row ) > end_date:
                        segment_end = segment_start + i
                        break
                    elif num_rows == segment_end+1:
                        segment_end = None
                        break

                segmented[ sname ] = self.rows[ segment_start:segment_end ]
                segment_start = segment_end

        return segmented
    
    def month( self ):
        years = self.end.year - self.start.year
        segmented = {}
        segment_start = 0
        for year in range( self.start.year, years ):
            pass
    
    def week( self ):
        pass
    
    def day( self ):
        pass

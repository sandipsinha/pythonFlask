__author__ = 'ssinha'
"""
" Copyright:    Loggly, Inc.
" Author:       Sandip Sinha
" Email:        ssinha@loggly.com
"
"""
from contextlib import contextmanager
from masterdb.config                          import CONNECTION_URL_FORMAT
from masterdb                                 import Masterdb
from law                        import config
from sqlalchemy                 import (create_engine, Column,
                                        Integer, DateTime, Date,
                                        Boolean, String,
                                        Numeric, ForeignKey,
                                        Index)
from sqlalchemy.dialects.mysql  import BIGINT, SMALLINT, MEDIUMINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import sessionmaker, relationship, backref
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

Base = declarative_base()
# Duplicate models of the same table need another base declaration
# so that they have a separate MetaData instance
OwnersBase = declarative_base()

db_url = '{dialect}://{user}:{passwd}@{host}:{port}/{dbname}'.format(
    dialect = config.get( 'salesorder', 'dialect' ),
    user    = config.get( 'salesorder', 'username' ),
    passwd  = config.get( 'salesorder', 'password' ),
    host    = config.get( 'salesorder', 'host' ),
    port    = config.get( 'salesorder', 'port' ),
    dbname  = config.get( 'salesorder', 'dbname' ),
)

engine = create_engine(
            db_url,
            echo=config.getboolean( 'salesorder', 'debug' ),
            pool_recycle=config.getint( 'salesorder', 'pool_recycle' ),
         )

Session = sessionmaker( bind=engine )

MDB = Masterdb( CONNECTION_URL_FORMAT % {'dialect':config.get( 'masterdb', 'dialect' ), 'host':config.get( 'masterdb', 'host' ),
                'user':config.get( 'masterdb', 'username' ), 'password':config.get( 'masterdb', 'password' ),
                'dbname':config.get( 'masterdb', 'dbname' ), 'port':config.get( 'masterdb', 'port' )})

class Salesorder( Base ):
    __tablename__  = 'sales_order'
    __table_args__ = {'mysql_engine':'InnoDB'}

    order_id          = Column( Integer, primary_key=True )
    volume            = Column( BIGINT )
    ret_days          = Column( Integer )
    plan_type         = Column( String(length=100) )
    tier_name         = Column( String(length=100) )
    acct_id           = Column( MEDIUMINT )
    billing_channel   = Column( String(length=100) )
    effective_date    = Column( Date )

    def __repr__(self):
        return "<salesorder({},{})>".format(
            self.order_id)


def create_salesorder_tables():
    """ Populates the sales order table """
    Base.metadata.create_all(
        bind=engine,
        tables=[
            Salesorder.__table__,
        ]
    )


@contextmanager
def session_context():
    session = Session()
    session._model_changes = {}
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
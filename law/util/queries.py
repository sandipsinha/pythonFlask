"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
" General purpose queries/query classes.
"
"""
from collections        import defaultdict
from datetime           import datetime, timedelta
from operator           import attrgetter
from sqlalchemy         import and_, or_, not_, func, distinct
from law.util.timeutil  import Timebucket
from sqlalchemy.sql import label, text
from law.util.adb       import session_context, AccountState, Owners, Tier, Users, Status, \
                        UserTracking, AccountProfile, DownGrades, AccountActivity, VolumeAccepted, \
                        ClusterToSubdomain, Account, engine

from law.util.tracerdb  import session_context as tdb
from law.util.tracerdb  import TracerBullet, TracerPercentiles, engine, TracerPercentilesCold, TracerBulletCold

from law.util.touchbiz import acct_id_for_subdomain
from sqlalchemy.orm.exc             import NoResultFound


def state_query( s, states, start, end, g2only=True):
    # operator | or's the states together ( | is overloaded in SQLAlchemy query construction)
    q = s.query( AccountState ) \
         .filter( AccountState.updated >= start ) \
         .filter( AccountState.updated < end ) \
         .filter( reduce( lambda query, func: query | func, [ AccountState.state.like( state ) for state in states] ) ) \

    if g2only:
        q = q.filter( AccountState.tPlan_id < 100 ) 

    return q

def query_state( states, start, end, g2only=True ):
    with session_context() as s:
        subs = state_query( s, states, start, end, g2only=g2only ).all()
        s.expunge_all()
    return subs

def query_product_state( states, products, start, end ):
    with session_context() as s:
        q = state_query( s, states, start, end )
        q = q.join( Tier, aliased=True )\
              .filter( or_(( Tier.name.__eq__( product ) for product in products )) )
        subs = q.all()
        s.expunge_all()
    return subs

def query_user_data(s, subdomain):
    q = s.query( Users, label('Number_Of_Logins', func.count(UserTracking.login)),
             label('Last_Login', func.max(UserTracking.login)))\
            .join( Status, and_( Users.acct_id == Status.acct_id)) \
            .join (UserTracking, and_( Users.user_id == UserTracking.user_id)) \
            .filter( and_(( Status.subdomain == subdomain )) ) \
            .group_by(Users.first_name,Users.last_name, Users.username, Users.email, Users.acct_id, Users.user_id)

    return q

def get_subd_names(subd):
    subdexp = '%' + subd + '%'
    querytorun='select distinct subdomain from accounts a where subdomain like :subexp limit 12'
    with session_context() as q:
        try:
            q = engine.execute(text(querytorun),subexp = subdexp )
            return q
        except NoResultFound as e:
                return None

def query_tracer_bullet(fdate, tdate, cluster, isithot):

    with tdb() as s:
        if isithot:
            q = s.query(TracerBullet)\
                .filter(TracerBullet.applies_start_time.between(fdate, tdate ))


            if cluster != '*':
                q.filter(TracerBullet.newcluster == cluster )
        else:
            q = s.query(TracerBulletCold)\
                .filter(TracerBulletCold.applies_start_time.between(fdate, tdate ))


            if cluster != '*':
                q.filter(TracerBulletCold.newcluster == cluster )
        datas = q.all()
        s.expunge_all()
    return datas

def query_tracer_percentile(fromDate, endDate , cluster, period, isithot):
    with tdb() as s:
        if isithot:
            q = s.query(TracerPercentiles) \
                .filter(and_(TracerPercentiles.start_date.between(fromDate, endDate ))) \
                .filter(TracerPercentiles.period == period)
            if cluster != '*':
                 q.filter(TracerPercentiles.repcluster == cluster )
        else:
            q = s.query(TracerPercentilesCold) \
                .filter(and_(TracerPercentilesCold.start_date.between(fromDate, endDate ))) \
                .filter(TracerPercentilesCold.period == period)
            if cluster != '*':
                 q.filter(TracerPercentilesCold.repcluster == cluster )

    datas = q.all()
    s.expunge_all()
    #import ipdb;ipdb.set_trace()
    return datas

def query_tracer_average(fromDate, endDate , period, isithot):

    with tdb() as s:
        if isithot:
            q = s.query(TracerPercentiles.start_date,label('average', func.avg(TracerPercentiles.pcnt_LT30)))\
                .filter(and_(TracerPercentiles.start_date.between(fromDate, endDate )))\
                .filter(TracerPercentiles.period == period)\
                .group_by(TracerPercentiles.start_date)
        else:
            q = s.query(TracerPercentilesCold.start_date,label('average', func.avg(TracerPercentilesCold.pcnt_LT30)))\
                .filter(and_(TracerPercentilesCold.start_date.between(fromDate, endDate )))\
                .filter(TracerPercentilesCold.period == period)\
                .group_by(TracerPercentilesCold.start_date)
        datas = q.all()
        s.expunge_all()
    return datas


def get_cluster_names(pref):
    clusterexp = '%' + pref + '%'
    querytorun='select distinct concat(a.cluster, substr(a.index_type,1)) newcluster, concat(a.cluster, substr(a.index_type,1,1)) clusterdata from tracer_percentiles a where ' \
               'concat(a.cluster, substr(a.index_type,1,1)) like :clsexp'
    with tdb() as q:
        try:
            q = engine.execute(text(querytorun),clsexp = clusterexp )
            return q
        except NoResultFound as e:
                return None

def query_subd_from_cluster(cluster):

    with session_context() as s:
        q = s.query(ClusterToSubdomain)\
            .filter(ClusterToSubdomain.cluster_type == cluster)

        datas = q.all()
        s.expunge_all()
    return datas


def query_user_state( subd ):
    with session_context() as s:
        users = query_user_data( s, subd).all()
        s.expunge_all()
    return users


def query_client_data(s, subd):
    # operator | or's the states together ( | is overloaded in SQLAlchemy query construction)
    #with session_context() as s:
    q = s.query( AccountProfile ) \
            .filter( ( AccountProfile.subdomain == subd ))
    return q



def query_client_state( subd ):
    with session_context() as s:
        clients = query_client_data( s, subd).one()
        s.expunge_all()
    return clients

def find_downgrade_weights():
    with session_context() as s:
        dg = s.query(DownGrades).filter(DownGrades.down_dt + 30 >= date.today() ).all()
        s.expunge_all
        riskarray = [{'subdomain':g.subdomain,'weight':g.down_wt} for g in dg]
    return riskarray

def get_total_recvd(acctid):
    with session_context() as s:
        smdata = s.query(label('total_bytes', func.sum(VolumeAccepted.bytes)))\
            .filter(VolumeAccepted.date + 30 >= date.today())\
            .filter(VolumeAccepted.acct_id == acctid).one()
        return smdata.total_bytes/30

def get_subscription_rate(subd):
    acct_id = acct_id_for_subdomain(subd)
    with session_context() as s:
        subsdata = s.query(label('Last Change Date', func.max(AccountActivity.created)),
                           label('current_subs', AccountActivity.to_vol_bytes))\
            .filter(AccountActivity.acct_id == acct_id).group_by(AccountActivity.acct_id).one()
        subsrate = subsdata.current_subs
        s.expunge_all
    averagedata = get_total_recvd(acct_id)
    if subsrate == 0:
        return 0
    percsentdata = float(averagedata)/subsrate
    if percsentdata >= .8:
        return 0
    elif percsentdata >= .6:
        return 5
    else:
        return 8

def get_user_count(subd):
    acct_id = acct_id_for_subdomain(subd)
    try:
        with session_context() as s:
            userdata = s.query(label('activecount',func.count(distinct(UserTracking.user_id))))\
                .filter(Users.user_id == UserTracking.user_id)\
                .filter(UserTracking.login + 30 >= date.today())\
                .filter(Users.acct_id == acct_id).one()
            usercnt = int(userdata.activecount)
            u = s.query(AccountProfile).filter(AccountProfile.subdomain == subd).one()
            ma = int(u.usercount)
            userpercent = float(usercnt)/ma
            s.expunge_all
        if userpercent >= .8:
            return 0
        elif userpercent >= .6:
            return 5
        else:
            return 8
    except NoResultFound:
        return 8

def get_cluster_details(subd):
    with session_context() as s:
        q = s.query(ClusterToSubdomain)\
            .filter(ClusterToSubdomain.subdomain == subd)

        datas = q.one()
        s.expunge_all()
    return datas

class QueryOwners(object):

    def __init__( self, states, start, end, owners=None ):
        self.states = states
        self.start  = start
        self.end    = end
        self.names  = owners

    def _query_owners( self, states, start, end, owners=None):
        with session_context() as s:
            subq = state_query( s, states, start, end ).subquery()
#            aliased_subq = aliased( AccountState, subq )
#            q = s.query( Owners, aliased_subq )\
            q = s.query( Owners, subq )\
                .join( subq, and_( Owners.acct_id == subq.c.acct_id,
                                    Owners.subdomain == subq.c.subdomain,
                                    func.DATE( subq.c.updated ) >= Owners.start_date,
                                    func.DATE( subq.c.updated ) <=  Owners.end_date ))

            # If we're only querying for specific users then apply the or'd constraints
            if owners != None:
                q.filter( reduce( lambda query, func: query | func, [ Owners.owner == owner for owner in owners] ) ) \

            subs = q.all()
            s.expunge_all()

        return subs

    @property
    def subs( self ):
        return self._query_owners( self.states, self.start, self.end, self.names )

    @property
    def owners( self ):
        owners = defaultdict( list )
        for row in self.subs:
            owners[ row.Owners.owner ].append( row )

        return owners

    def bucketed( self, bucket ):
        bucket_func = attrgetter( bucket )

        owners = self.owners
        for name in owners:
            owners[name] = bucket_func( Timebucket( owners[name], 'updated' ) )()

        return owners






import unittest
from law.web import app as mainc
from law.util import adb
from tests.fixtures import populate
from law.util.queries import query_user_data
from datetime import datetime






def fixtures():
    teardown_module()
    adb.Base.metadata.create_all(
        bind=adb.engine,
        tables = [
            adb.Users.__table__,
            adb.UserTracking.__table__,
            adb.Status.__table__,
        ]
    )

    with adb.session_context() as s:
        populate( s, model_names=[
                        'Users',
                        'UserTracking',
                        'Status',]

        )


def setup_module():
    fixtures()

def teardown_module():
    drop_tables()


def drop_tables():
    adb.Base.metadata.drop_all(
        bind=adb.engine,
        tables=[
            adb.Users.__table__,
            adb.UserTracking.__table__,
            adb.Status.__table__,
        ]
    )


class TestUserDataInfo( unittest.TestCase ):



    def create_app(self):
        app = mainc.test_client()
        return app


    def test_userinfo_form(self):
        app=self.create_app()
        params = {'subdomain':'gifted.sportsperson'}
        response = app.get('/user/gifted.sportsperson')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.index('email') > 0, True)

    def test_userinfo_data(self):
        subd = 'talented.scientist'

        with adb.loader() as s:
            users = query_user_data(s, subd)
            userdata = users.all()
            s.expunge_all()
        self.assertEqual(len(userdata), 2)
        self.assertEqual('albert.einstein@loggly.com' , userdata[1].Users.email)
        self.assertEqual(str(userdata[0].Last_Login.strftime('%Y/%m/%d')),'2012/06/09' )

        subd = 'gifted.sportsperson'

        with adb.loader() as s:
            users = query_user_data(s, subd)
            userdata = users.all()


        self.assertEqual(len(userdata), 1)
        self.assertEqual('carl.lewis@loggly.com' , userdata[0].Users.email)
        self.assertEqual(str(userdata[0].Last_Login.strftime('%Y/%m/%d')),'2015/07/09' )

        subd = 'crafty.politicians'
        #Now test users who do not have any names
        with adb.loader() as s:
            users = query_user_data(s, subd)
            userdata = users.all()
        import ipdb;ipdb.set_trace()
        try:
            self.assertEqual(len(userdata), 1)
            self.assertEqual(' ' , userdata[0].Users.name)
            #The Attribute error trap is raised to make sure that there is no name field in the dataset
        except AttributeError:
            self.assertEqual('narendra.modi@loggly.com' , userdata[0].Users.email)


















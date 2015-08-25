import unittest
from law.web import app as mainc
from law.util import adb
from tests.fixtures import populate
from flask import json




def fixtures():
    teardown_module()
    adb.Base.metadata.create_all(
        bind=adb.engine,
        tables = [
            adb.AccountProfile.__table__,
        ]
    )

    with adb.session_context() as s:
        populate( s, model_names=[
                        'AccountProfile',
                        ]

        )


def setup_module():
    fixtures()

def teardown_module():
    drop_tables()


def drop_tables():
    adb.Base.metadata.drop_all(
        bind=adb.engine,
        tables=[
            adb.AccountProfile.__table__,
        ]
    )


class TestClientAPI( unittest.TestCase ):



    def create_app(self):
        app = mainc.test_client()
        return app


    def test_client_api(self):
        app=self.create_app()
        response =   app.get('/apiv1/clientinfo/sfdcapi/1001')

        self.assertEqual(response.status_code, 200)
        respdata = json.loads(response.data)
        self.assertEqual(respdata['acct_id'], 1001)
        self.assertEqual(respdata['rulescount'], 2)
        self.assertEqual(respdata['groupcount'], 5)
        self.assertEqual(respdata['usercount'], 7)

        response =   app.get('/apiv1/clientinfo/sfdcapi/1000')

        self.assertEqual(response.status_code, 200)
        respdata = json.loads(response.data)
        self.assertEqual(respdata['acct_id'], 1000)
        self.assertEqual(respdata['rulescount'], 9)
        self.assertEqual(respdata['groupcount'], 7)
        self.assertEqual(respdata['usercount'], 5)

        response =   app.get('/apiv1/clientinfo/sfdcapi/1002')

        self.assertEqual(response.status_code, 200)
        respdata = json.loads(response.data)
        self.assertEqual(respdata['acct_id'], 1002)
        self.assertEqual(respdata['rulescount'], 1)
        self.assertEqual(respdata['groupcount'], 2)
        self.assertEqual(respdata['usercount'], 3)



















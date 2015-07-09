import unittest
from mock import patch
from law.web import app as mainc
from datetime import date
import json
from tests.fixtures import populate
from law.web.salesorder import model as salesdb
from law.web.salesorder.model import session_context, Salesorder






def fixtures():
    drop_tables()
    salesdb.Base.metadata.create_all(
    bind=salesdb.engine,
    tables = [
        salesdb.Salesorder.__table__,
    ]
    )

    with salesdb.session_context() as s:
        populate( s, model_names=['Salesorder'] )


def setup_module():
    fixtures()

def teardown_module():
    pass


def drop_tables():
    salesdb.Base.metadata.drop_all(
        bind=salesdb.engine,
        tables=[
            salesdb.Salesorder.__table__,
        ]
    )

datap={'update':{
        'order_id'       : 959,
        'volume'         : 500,
        'ret_days'       : 10,
        'plan_type'      : 'Pro Plan',
        'tier_name'      : 'Top tier 10',
        'subdomain'       : 'Test Mock1',
        'billing_channel': 'Channel Test',
        'effective_date' :  date( 2016, 06, 15 ),
        'Update'         : 'Update'
         },
        'Add':[{
        'volume'         : 500,
        'ret_days'       : 10,
        'plan_type'      : 'Pro Plan',
        'tier_name'      : 'Top tier 10',
        'subdomain'       : 'Test Mock4',
        'billing_channel': 'Channel Test',
        'effective_date' :  date( 2016, 06, 15 ),
        'Update'         : 'Add'
         },
         {
        'volume'         : 500,
        'ret_days'       : 10,
        'plan_type'      : 'Pro Plan',
        'tier_name'      : 'Top tier 10',
        'subdomain'       : 'Test Mock4',
        'billing_channel': 'Channel Test',
        'effective_date' :  date( 2016, 06, 15 ),
        'Update'         : 'Add'
         }
         ] }


class TestSalesOrderApp( unittest.TestCase ):



    def create_app(self):
        app = mainc.test_client()
        return app


    def test_salesorder_form(self):
        app=self.create_app()
        with patch('masterdb.Masterdb.get_loggly_name') as mock1:
            mock1.return_value = 'testdomain'
            response = app.post('/salesorder/', data=dict(order_id=958, lookup = 'lookup'))
            self.assertEqual(response.status_code, 200)
            self.assertIn('Channel 2', response.data)

    def test_add_subdoamin(self):
        app=self.create_app()
        with patch('masterdb.Masterdb.get_loggly_id') as mock1:
            mock1.return_value = 10001
            response = app.post('/salesorder/orderdetails', data=datap['Add'][1])
            self.assertEqual(response.status_code, 200)
            self.assertIn('The order was added', response.data)

    def test_update_salesorder(self):
         app=self.create_app()
         with patch('masterdb.Masterdb.get_loggly_id') as mock1:
             mock1.return_value = 10001
             response = app.post('/salesorder/orderdetails', data=datap['update'])
             self.assertEqual(response.status_code, 200)
             with session_context() as s:
                  sord = s.query( Salesorder) \
                         .filter( Salesorder.order_id==959)
             res = sord.first()
             if res is not None:
                 self.assertEqual(res.tier_name,'Top tier 10')
                 self.assertEqual(res.billing_channel,'Channel Test')

    def test_wrong_id(self):
        app=self.create_app()
        response = app.post('/salesorder/', data=dict(order_id=1001, lookup = 'lookup'))
        self.assertIn('Enter a valid value of Order ID or Sub-Domain', response.data)



    def test_add_wrong_subdoamin(self):
        app=self.create_app()
        with patch('masterdb.Masterdb.get_loggly_id') as mock1:
            mock1.return_value = None
            response = app.post('/salesorder/orderdetails', data=datap['Add'][0])
            self.assertEqual(response.status_code, 200)
            self.assertIn('Invalid sub doamin specified. The order was not added', response.data)














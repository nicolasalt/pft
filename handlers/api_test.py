import unittest
import datetime
from google.appengine.api import users
from google.appengine.ext import testbed, ndb
import controller
from datastore import models
import webtest


class GetProfileTestCase(unittest.TestCase):
  def setUp(self):
    self.testapp = webtest.TestApp(controller.app)

    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_user_stub()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.maxDiff = None

    self.now = datetime.datetime(2010, 12, 27)
    ndb.DateTimeProperty._now = lambda _: self.now

  def _SetUser(self):
    self.google_user = users.User(email='foo@example.com', _user_id='10001')
    self.visitor_id = self.google_user.user_id()
    self.testbed.setup_env(
      USER_EMAIL=self.google_user.email(),
      USER_ID=self.google_user.user_id(),
      overwrite=True)

  def testVisitorNotLoggedIn(self):
    response = self.testapp.get('/api/get_active_profile')

    self.assertEqual(
      {
        'status': 'not_logged_in',
        'login_url': 'https://www.google.com/accounts/Login?continue='
                      'http%3A//testbed.example.com/'
      },
      response.json)

  def testNoProfile(self):
    self._SetUser()
    response = self.testapp.get('/api/get_active_profile')

    self.assertEqual(
      {
        'status': 'profile_not_selected'
      },
      response.json)

  def testNormal(self):
    self._SetUser()

    profile = models.Profile.Create(self.visitor_id, 'Test profile name')
    visitor = models.User.Get(self.visitor_id)
    visitor.active_profile_id = profile.key.id()
    visitor.put()

    profile.AddAccount(name='Test account1', currency='USD', balance=10.0)
    profile.AddAccount(name='Test account2', currency='CHF', balance=20.0)
    profile.AddCategory(name='Test category1', balance=5.0)
    profile.AddCategory(name='Test category2', balance=6.0)

    models.CurrencyRates.Update({
      'usd': 1.0,
      'chf': 1.5
    })

    response = self.testapp.get('/api/get_active_profile')

    self.assertEqual(
      {'profile': {
        'accounts': [
          {'balance': 10.0,
           'creation_time': '2010-12-27T00:00:00',
           'currency': 'USD',
           'id': 0,
           'name': 'Test account1'},
          {'balance': 20.0,
           'creation_time': '2010-12-27T00:00:00',
           'currency': 'CHF',
           'id': 1,
           'name': 'Test account2'}],
        'categories': [
          {'balance': 5.0,
           'creation_time': '2010-12-27T00:00:00',
           'id': 0,
           'name': 'Test category1'},
          {'balance': 6.0,
           'creation_time': '2010-12-27T00:00:00',
           'id': 1,
           'name': 'Test category2'}],
        'creation_time': '2010-12-27T00:00:00',
        'id': 1,
        'main_currency': 'USD',
        'name': 'Test profile name',
        'owner_id': '10001',
        'parse_schemas': [],
        'user_ids': ['10001']},
       'total_balance': 40.0,
       'user_profile_settings': {
         'cash_account_id': None,
         'important_account_ids': [],
         'main_account_id': None,
         'profile_id': 1},
       'visitor': {
         'active_profile_id': 1,
         'creation_time': '2010-12-27T00:00:00',
         'id': '10001',
         'profile_settings': [
           {'cash_account_id': None,
            'important_account_ids': [],
            'main_account_id': None,
            'profile_id': 1}]}},
      response.json)

  def tearDown(self):
    self.testbed.deactivate()


if __name__ == '__main__':
  unittest.main()

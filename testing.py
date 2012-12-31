import unittest
import datetime
from google.appengine.api import users
from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import testbed, ndb
import mox
import controller
import webtest
from datastore import models


class BaseTestCase(unittest.TestCase):
  def setUp(self):
    self.testapp = webtest.TestApp(controller.app)

    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_user_stub()
    self.testbed.init_datastore_v3_stub(
      consistency_policy=datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0))
    self.testbed.init_memcache_stub()
    self.maxDiff = None

    self.now = datetime.datetime(2010, 12, 27)
    ndb.DateTimeProperty._now = lambda _: self.now

    self.mox = mox.Mox()

    self.google_user = users.User(email='foo@example.com', _user_id='10001')
    self.google_user2 = users.User(email='foo2@example.com', _user_id='10002')
    self.LogIn(self.google_user)

    models.CurrencyRates.Update({
      'usd': 1.0,
      'chf': 1.5,
      'rub': 0.03
    })

  def LogIn(self, user):
    self.visitor_id = user.user_id()
    self.testbed.setup_env(USER_EMAIL=user.email(), USER_ID=user.user_id(), overwrite=True)

  def AddProfile(self):
    self.profile = models.Profile.Create(self.visitor_id, name='Test profile')
    models.User.Update(self.visitor_id, active_profile_id=self.profile.key.id())

  def AddAccountsAndCategories(self):
    profile = models.Profile.GetActive(self.visitor_id)
    self.profile_id = profile.key.id()
    self.account1_id = profile.AddAccount(name='Test account1', currency='USD').id
    self.account2_id = profile.AddAccount(name='Test account2', currency='CHF').id
    self.category1_id = profile.AddCategory(name='Test category1').id
    self.category2_id = profile.AddCategory(name='Test category2').id

  def tearDown(self):
    self.mox.UnsetStubs()
    self.testbed.deactivate()

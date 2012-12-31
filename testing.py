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
      consistency_policy=datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1))
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

  def tearDown(self):
    self.mox.UnsetStubs()
    self.testbed.deactivate()

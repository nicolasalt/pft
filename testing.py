import unittest
import datetime
from google.appengine.api import users
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
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.maxDiff = None

    self.now = datetime.datetime(2010, 12, 27)
    ndb.DateTimeProperty._now = lambda _: self.now

    self.mox = mox.Mox()

    self.google_user = users.User(email='foo@example.com', _user_id='10001')
    self.visitor_id = self.google_user.user_id()
    self.testbed.setup_env(
      USER_EMAIL=self.google_user.email(),
      USER_ID=self.google_user.user_id(),
      overwrite=True)

    models.CurrencyRates.Update({
      'usd': 1.0,
      'chf': 1.5,
      'rub': 0.03
    })

  def AddProfile(self):
    self.profile = models.Profile.Create(self.visitor_id, 'Test profile')
    models.User.Update(self.visitor_id, active_profile_id=self.profile.key.id())

  def tearDown(self):
    self.mox.UnsetStubs()
    self.testbed.deactivate()

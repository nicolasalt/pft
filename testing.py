import unittest
import datetime
from google.appengine.api import users
from google.appengine.ext import testbed, ndb
import mox
import controller
import webtest


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

  def tearDown(self):
    self.mox.UnsetStubs()
    self.testbed.deactivate()

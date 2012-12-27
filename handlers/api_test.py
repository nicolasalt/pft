import unittest
from google.appengine.ext import testbed
import controller
from handlers import api
import webtest


class GetProfileTestCase(unittest.TestCase):
  def setUp(self):
    self.testapp = webtest.TestApp(controller.app)

    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_user_stub()

  def testVisitorNotLoggedIn(self):
    response = self.testapp.get('/api/get_profile')

    self.assertEqual(302,response.status_int)


if __name__ == '__main__':
  unittest.main()

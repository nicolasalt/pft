import unittest
from google.appengine.ext import testbed
import controller
from handlers import api
import webtest


class GetProfileTestCase(unittest.TestCase):
  def test_normal(self):
    self.testapp = webtest.TestApp(controller.app)

    self.testbed = testbed.Testbed()
    self.testbed.activate()

    response = self.testapp.get('/api/get_profile')

    self.assertEqual('',response)



if __name__ == '__main__':
  unittest.main()

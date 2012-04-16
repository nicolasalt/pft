import unittest
from google.appengine.api import urlfetch
from datastore import models
import mox
from util import currency_rates_util


class ParseFromJsonTestCase(unittest.TestCase):
  def test_normal(self):
    parsed_rate = currency_rates_util._ParseRateFromJson(
        '{lhs: "1 Russian ruble",rhs: "0.033616 U.S. dollars",error: "",'
        'icc: true}')
    self.assertAlmostEqual(0.033616, parsed_rate)

    parsed_rate = currency_rates_util._ParseRateFromJson(
        '{lhs: "1 U.S. dollar",rhs: "1 U.S. dollar",error: "0",icc: true}')
    self.assertAlmostEqual(1.0, parsed_rate)

if __name__ == '__main__':
  unittest.main()


class GetFreshRatesTestCase(unittest.TestCase):
  class FakeResponse(object):
    def __init__(self, content):
      self.content = content

  def setUp(self):
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(urlfetch, 'fetch')

    self.old_supported_currencies = models.CurrencyRates.SUPPORTED_CURRENCIES

    models.CurrencyRates.SUPPORTED_CURRENCIES = ['usd', 'euro', 'rub']

  def test_normal(self):
    urlfetch.fetch(
        'http://www.google.com/ig/calculator?hl=en&q=1usd=?usd').AndReturn(
            GetFreshRatesTestCase.FakeResponse(
            '{lhs: "1 U.S. dollar",rhs: "1 U.S. dollar",error: "0",icc: true}'))
    urlfetch.fetch(
        'http://www.google.com/ig/calculator?hl=en&q=1euro=?usd').AndReturn(
            GetFreshRatesTestCase.FakeResponse(
            '{lhs: "1 Euro",rhs: "1.3015 U.S. dollars",error: "",icc: true}'))
    urlfetch.fetch(
        'http://www.google.com/ig/calculator?hl=en&q=1rub=?usd').AndReturn(
            GetFreshRatesTestCase.FakeResponse(
                'error'))

    self.mox.ReplayAll()
    rates = currency_rates_util.GetFreshRates()
    self.mox.VerifyAll()

    self.assertDictEqual({'euro': 1.3015, 'usd': 1}, rates)

  def tearDown(self):
    models.CurrencyRates.SUPPORTED_CURRENCIES = self.old_supported_currencies
    self.mox.UnsetStubs()

if __name__ == '__main__':
  unittest.main()

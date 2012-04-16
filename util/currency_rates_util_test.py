import unittest
import urllib2
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
  def setUp(self):
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(urllib2, 'urlopen')

    self.old_supported_currencies = models.CurrencyRates.SUPPORTED_CURRENCIES

    models.CurrencyRates.SUPPORTED_CURRENCIES = ['usd', 'euro']

  def test_normal(self):
    urllib2.urlopen(
        'http://www.google.com/ig/calculator?hl=en&q=1usd=?usd').AndReturn(
            '{lhs: "1 U.S. dollar",rhs: "1 U.S. dollar",error: "0",icc: true}')
    urllib2.urlopen(
        'http://www.google.com/ig/calculator?hl=en&q=1euro=?usd').AndReturn(
            '{lhs: "1 Euro",rhs: "1.3015 U.S. dollars",error: "",icc: true}')

    self.mox.ReplayAll()
    rates = currency_rates_util.GetFreshRates()
    self.mox.VerifyAll()

    self.assertDictEqual({'euro': 1.3015, 'usd': 1}, rates)

  def tearDown(self):
    models.CurrencyRates.SUPPORTED_CURRENCIES = self.old_supported_currencies
    self.mox.UnsetStubs()

if __name__ == '__main__':
  unittest.main()

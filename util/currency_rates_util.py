import re
import urllib2
from datastore import models

def _ParseRateFromJson(text):
  matchObject = re.search('rhs:\s*"(\d+\.?\d*)', text)
  if matchObject:
    return float(matchObject.group(1))
  else:
    return None


def GetFreshRates():
  rates = {}
  for currency in models.CurrencyRates.SUPPORTED_CURRENCIES:
    url = 'http://www.google.com/ig/calculator?hl=en&q=1%s=?usd' % currency
    try:
      result = urllib2.urlopen(url)
      rates[currency] = _ParseRateFromJson(result)
    except urllib2.URLError:
      pass

  return rates

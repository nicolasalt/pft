import re
from google.appengine.api import urlfetch
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
    result = urlfetch.fetch(url)
    rate = _ParseRateFromJson(result.content)
    if rate is not None:
      rates[currency] = rate

  return rates

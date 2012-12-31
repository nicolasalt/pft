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


def GetCachedRates():
  ratesModel = models.CurrencyRates.Get()
  return dict([(r.currency, r.rate) for r in ratesModel.rates])


def IsCurrencySupported(currency):
  return currency and currency.lower() in GetCachedRates().iterkeys()


def CalculateCurrencySum(amount_list, main_currency):
  """
    Args:
      amount_list: list like [(3.4, 'usd'), (5.6, 'euro')]
  """
  total_sum = 0
  for amount, currency in amount_list:
    total_sum += ConvertCurrency(amount, currency, main_currency)

  return total_sum


def ConvertCurrency(amount, source_currency, dest_currency):
  rates = GetCachedRates()
  source_currency = source_currency.lower()
  dest_currency = dest_currency.lower()
  if source_currency not in rates:
    raise ValueError('Unsupported source_currency %r' % source_currency)
  if dest_currency not in rates:
    raise ValueError('Unsupported dest_currency %r' % dest_currency)

  return amount * rates[source_currency] / rates[dest_currency]

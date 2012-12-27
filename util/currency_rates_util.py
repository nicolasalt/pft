import re
from google.appengine.api import urlfetch
from datastore import models, lookup

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


def CalculateCurrencySum(amount_list, main_currency):
  """
    Args:
      amount_list: list like [(3.4, 'usd'), (5.6, 'euro')]
  """
  rates = GetCachedRates()
  main_currency = main_currency.lower()
  if main_currency not in rates:
    return None

  main_currency_rate = rates[main_currency]
  total_sum = 0
  for amount, currency in amount_list:
    currency = currency.lower()
    if currency in rates:
      total_sum += amount * rates[currency] / main_currency_rate

  return total_sum

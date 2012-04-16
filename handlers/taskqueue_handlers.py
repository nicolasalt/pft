from google.appengine.api.taskqueue import taskqueue
from common import CommonHandler
from datastore import update
from util import currency_rates_util

class UpdateCurrencyRates(CommonHandler):
  def HandlePost(self):
    update.UpdateCurrencyRates(currency_rates_util.GetFreshRates())

    # Schedules itself to run in a day
    taskqueue.add(url='/task/update_currency_rates', countdown=86400)

from google.appengine.api.taskqueue import taskqueue
import webapp2
from datastore import update
from util import currency_rates_util

class UpdateCurrencyRates(webapp2.RequestHandler):
  def post(self):
    update.UpdateCurrencyRates(currency_rates_util.GetFreshRates())

    # Schedules itself to run in a day
    taskqueue.add(url='/task/update_currency_rates', countdown=86400)

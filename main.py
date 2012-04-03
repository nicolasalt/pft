import datetime
import webapp2
import jinja2
import os

from google.appengine.ext import ndb
from google.appengine.api import users
from datastore import models, lookup

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
  def get(self):
    visitor = users.get_current_user()
    if not visitor:
      self.redirect(users.create_login_url(self.request.uri))

    user_settings = lookup.GetOrCreateUserSettings(visitor)

    account_query = models.Account.query(
        ancestor=user_settings.key).order(-models.Account.date)
    accounts = account_query.fetch(100)

    transaction_query = models.Transaction.query(
        ancestor=user_settings.key).order(-models.Transaction.date)
    transactions = transaction_query.fetch(100)

    template_values = {
        'user_settings': user_settings,
        'accounts': accounts,
        'transactions': transactions
    }

    template = jinja_environment.get_template('templates/index.html')
    self.response.out.write(template.render(template_values))


class DoAddAccount(webapp2.RequestHandler):
  def post(self):
    visitor = users.get_current_user()
    if not visitor:
      self.redirect(users.create_login_url(self.request.uri))

    user_settings = lookup.GetOrCreateUserSettings(visitor)

    account = models.Account(
        parent=user_settings.key,
        owner=users.get_current_user(),
        name=self.request.get('name'),
        currency= self.request.get('currency')).put()

    self.redirect('/')


@ndb.transactional
def AddTransaction(user_settings, account_id, amount, date):
  account = models.Account.get_by_id(account_id, parent=user_settings.key)
  transaction = models.Transaction(
    parent=user_settings.key,
    account_id=account.key.id(),
    amount=amount,
    date=date).put()
  account.balance -= amount
  account.put()


class DoAddTransaction(webapp2.RequestHandler):
  def post(self):
    visitor = users.get_current_user()
    if not visitor:
      self.redirect(users.create_login_url(self.request.uri))

    user_settings = lookup.GetOrCreateUserSettings(visitor)
    amount = float(self.request.get('amount'))
    account_id = int(self.request.get('account_id'))

    AddTransaction(user_settings, account_id,
                   amount, datetime.datetime.now())

    self.redirect('/')


class DoEditUserSettings(webapp2.RequestHandler):
  def post(self):
    visitor = users.get_current_user()
    if not visitor:
      self.redirect(users.create_login_url(self.request.uri))

    user_settings = lookup.GetOrCreateUserSettings(visitor)
    main_currency = self.request.get('main_currency')
    if main_currency:
      user_settings.main_currency = main_currency
      user_settings.put()

    self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/do/add_account', DoAddAccount),
    ('/do/add_transaction', DoAddTransaction),
    ('/do/edit_user_settings', DoEditUserSettings)],
    debug=True)

import datetime
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users
from datastore import models, lookup


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
def AddTransaction(user_settings, account_id, amount, date, category_id):
  account = models.Account.get_by_id(account_id, parent=user_settings.key)
  transaction = models.Transaction(
    parent=user_settings.key,
    account_id=account.key.id(),
    amount=amount,
    date=date)
  if category_id:
    transaction.category_id = category_id
    category = models.Category.get_by_id(category_id, parent=user_settings.key)
    category.balance -= amount
    category.put()
  transaction.put()
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
    date = datetime.datetime.strptime(self.request.get('date'), '%m/%d/%Y')
    raw_category_id = self.request.get('category_id')
    category_id = None
    if raw_category_id:
      category_id = int(raw_category_id)

    AddTransaction(user_settings, account_id,
                   amount, date, category_id)

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


class DoAddCategory(webapp2.RequestHandler):
  def post(self):
    visitor = users.get_current_user()
    if not visitor:
      self.redirect(users.create_login_url(self.request.uri))

    user_settings = lookup.GetOrCreateUserSettings(visitor)
    name = self.request.get('name')

    account = models.Category(
      parent=user_settings.key,
      name=name).put()

    self.redirect('/edit_budget')


class DoEditBudget(webapp2.RequestHandler):
  def post(self):
    visitor = users.get_current_user()
    if not visitor:
      self.redirect(users.create_login_url(self.request.uri))

    user_settings = lookup.GetOrCreateUserSettings(visitor)

    budget_date = datetime.datetime.strptime(
      self.request.get('budget_date'), '%m.%Y')

    category_id_and_amount = []
    for arg in self.request.arguments():
      if arg.startswith('category_') and self.request.get(arg):
        category_id = int(arg[9:])
        category_id_and_amount.append(
            (category_id, float(self.request.get(arg))))

    budget_key = ndb.Key(models.Budget, budget_date.strftime('%m.%Y'))
    budget = models.Budget.get_or_insert(
        budget_key.id(), parent=user_settings.key, date=budget_date)
    budget.expenses = [models.ExpenseItem(category_id=cat_id,
                                          planned_value=amount)
                       for cat_id, amount in category_id_and_amount]
    budget.put()

    self.redirect('/edit_budget')

import csv
from datetime import datetime
import io

from google.appengine.ext import ndb
from google.appengine.api import users
from common_handlers import CommonHandler
from datastore import models, lookup, update


class DoAddAccount(CommonHandler):
  def HandlePost(self):
    name = self.request.get('name')
    currency = self.request.get('currency')
    update.AddAccount(self.profile, name, currency)

    self.redirect('/')


class DoAddTransaction(CommonHandler):
  def HandlePost(self):
    amount = float(self.request.get('amount'))
    description = self.request.get('description')
    account_id = int(self.request.get('account_id'))
    date = datetime.strptime(self.request.get('date'), '%m/%d/%Y')
    raw_category_id = self.request.get('category_id')
    category_id = None
    if raw_category_id:
      category_id = int(raw_category_id)

    update.AddTransaction(self.profile, account_id,
                          amount, date, category_id, description)

    self.redirect('/')


class DoAddTransactionsFromCsv(CommonHandler):
  def HandlePost(self):
    account_id = int(self.request.get('account_id'))
    raw_csv = self.request.get('csv')
    schema = ['date', 'description', None, None, 'debit', 'credit']

    for row in csv.DictReader(raw_csv.splitlines(), schema):
      try:
        date = datetime.strptime(row['date'], '%d.%m.%Y')
        if row['debit'] or row['credit']:
          if row['debit']:
            amount = float(row['debit'])
          else:
            amount = -float(row['credit'])
          update.AddTransaction(self.profile, account_id,
                                amount, date, None, row['description'])
      except ValueError:
        pass

#    self.redirect('/')


class DoEditProfile(CommonHandler):
  def HandlePost(self):
    main_currency = self.request.get('main_currency')
    password = self.request.get('password')

    kw = {}
    if main_currency:
      kw['main_currency'] = main_currency
    if password:
      kw['password'] = password

    update.UpdateProfile(self.profile, **kw)

    self.redirect('/user_settings')


class DoAddProfile(CommonHandler):
  def post(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    profile_name = self.request.get('name')

    self.profile = update.AddProfile(self.google_user, profile_name)
    update.UpdateUser(self.visitor, active_profile_id=self.profile.key.id())

    self.redirect('/')


class DoConnectToProfile(CommonHandler):
  def post(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    profile_code = self.request.get('profile_code')

    if profile_code:
      self.profile = lookup.GetProfileByCode(profile_code)
      if self.profile:
        update.AddUserToProfile(self.profile, self.google_user)
        update.UpdateUser(self.visitor, active_profile_id=self.profile.key.id())

    self.redirect('/')


class DoSetActiveProfile(CommonHandler):
  def post(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    profile_id = int(self.request.get('id'))

    if lookup.GetProfileById(profile_id):
      update.UpdateUser(self.visitor, active_profile_id=profile_id)
    else:
      raise Exception('Profile with id %r does not exist' % profile_id)

    self.redirect('/')


class DoAddCategory(CommonHandler):
  def HandlePost(self):
    name = self.request.get('name')

    account = models.Category(
      parent=self.profile.key,
      name=name).put()

    self.redirect('/edit_budget')


class DoEditBudget(CommonHandler):
  def HandlePost(self):
    budget_date = datetime.strptime(
      self.request.get('budget_date'), '%m.%Y')

    category_id_and_amount = []
    for arg in self.request.arguments():
      if arg.startswith('category_') and self.request.get(arg):
        category_id = int(arg[9:])
        category_id_and_amount.append(
            (category_id, float(self.request.get(arg))))

    budget_key = ndb.Key(models.Budget, budget_date.strftime('%m.%Y'))
    budget = models.Budget.get_or_insert(
        budget_key.id(), parent=self.profile.key, date=budget_date)
    budget.expenses = [models.ExpenseItem(category_id=cat_id,
                                          planned_value=amount)
                       for cat_id, amount in category_id_and_amount]

    if self.request.get('new_incomeitem_name'):
      new_income_item_name = self.request.get('new_incomeitem_name')
      new_income_item_value = float(self.request.get('new_incomeitem_value'))
      budget.income.append(models.IncomeItem(
          name=new_income_item_name, planned_value=new_income_item_value))

    budget.put()

    self.redirect('/edit_budget')

from datetime import datetime

from google.appengine.ext import ndb
from common_handlers import CommonHandler
from datastore import models, lookup, update
import parse


class DoAddAccount(CommonHandler):
  def HandlePost(self):
    name = self.request.get('name')
    currency = self.request.get('currency')
    update.AddAccount(self.profile, name, currency)

    self.redirect('/')


class DoEditTransaction(CommonHandler):
  def _UpdateBudget(self, budget_date, transaction):
    budget_key = ndb.Key(models.Budget, models.Budget.DateToStr(budget_date))
    budget = models.Budget.get_or_insert(
      budget_key.id(), parent=self.profile.key, date=budget_date)
    budget_items = [i for i in budget.items
                    if i.transaction_id == transaction.key.id()]
    if len(budget_items) == 1:
      budget_item = budget_items[0]
    else:
      budget_item = models.BudgetItem(
        date=transaction.date, transaction_id=transaction.key.id())
      budget.items.append(budget_item)
    budget_item.date = transaction.date
    budget_item.description = transaction.description
    budget_item.category_id = transaction.category_id
    budget_item.planned_amount = transaction.amount
    budget.put()

  def HandlePost(self):
    amount = parse.ParseFloat(self.request.get('amount'))
    description = self.request.get('description')
    date = datetime.strptime(self.request.get('date'), '%d.%m.%Y')
    account_id = parse.ParseInt(self.request.get('account_id'))
    category_id = parse.ParseInt(self.request.get('category_id'))
    dest_category_id = parse.ParseInt(self.request.get('dest_category_id'))
    dest_account_id = parse.ParseInt(self.request.get('dest_account_id'))
    transaction_id = parse.ParseInt(self.request.get('transaction_id'))

    raw_budget_date = self.request.get('budget_date')
    budget_date = None
    if raw_budget_date:
      budget_date = models.Budget.ParseDate(raw_budget_date)
      date = budget_date.replace(day=date.day)

    source = 'budget' if budget_date else 'manual'

    if transaction_id is not None:
      transaction = update.UpdateTransaction(
          self.profile, transaction_id, amount, date, account_id=account_id,
          category_id=category_id, description=description,
          dest_category_id=dest_category_id, dest_account_id=dest_account_id,
          source=source, planned=budget_date is not None)
    else:
      transaction = update.AddTransaction(
          self.profile, amount, date, account_id=account_id,
          category_id=category_id, description=description,
          dest_category_id=dest_category_id, dest_account_id=dest_account_id,
          source=source, planned=budget_date is not None)

    if budget_date:
      self._UpdateBudget(budget_date, transaction)

    self.response.set_status(200)


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

    update.AddCategory(self.profile, name)

    self.redirect('/')

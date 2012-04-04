import datetime

from google.appengine.ext import ndb
from google.appengine.api import users
from common_handlers import CommonHandler
from datastore import models, lookup


class DoAddAccount(CommonHandler):
  def handle_post(self):
    account = models.Account(
        parent=self.user_settings.key,
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


class DoAddTransaction(CommonHandler):
  def handle_post(self):
    amount = float(self.request.get('amount'))
    account_id = int(self.request.get('account_id'))
    date = datetime.datetime.strptime(self.request.get('date'), '%m/%d/%Y')
    raw_category_id = self.request.get('category_id')
    category_id = None
    if raw_category_id:
      category_id = int(raw_category_id)

    AddTransaction(self.user_settings, account_id,
                   amount, date, category_id)

    self.redirect('/')


class DoEditUserSettings(CommonHandler):
  def handle_post(self):
    main_currency = self.request.get('main_currency')
    password = self.request.get('password')
    if main_currency:
      self.user_settings.main_currency = main_currency
    if password:
      self.user_settings.password = password

    self.user_settings.put()

    self.redirect('/user_settings')


class DoCreateUser(CommonHandler):
  def post(self):
    self.visitor = users.get_current_user()
    if not self.visitor:
      self.redirect(users.create_login_url(self.request.uri))

    self.user_settings = lookup.GetUserSettings(self.visitor)
    if self.user_settings:
      self.redirect('/')

    existing_account_email = self.request.get('existing_account_email')
    if existing_account_email:
      existing_account_password = self.request.get('existing_account_password')
      existing_user = users.User(existing_account_email)
      self.user_settings = lookup.GetUserSettings(existing_user)
      if (not self.user_settings or
          existing_account_password != self.user_settings.password):
        self.redirect('/')
        return

    else:
      self.user_settings = models.UserSettings(
          id=self.visitor.user_id())

    self.user_settings.users.append(self.visitor)
    self.user_settings.put()

    self.redirect('/')


class DoAddCategory(CommonHandler):
  def handle_post(self):
    name = self.request.get('name')

    account = models.Category(
      parent=self.user_settings.key,
      name=name).put()

    self.redirect('/edit_budget')


class DoEditBudget(CommonHandler):
  def handle_post(self):
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
        budget_key.id(), parent=self.user_settings.key, date=budget_date)
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

import datetime
from google.appengine.api import users
from google.appengine.ext import ndb

from common_handlers import CommonHandler
from datastore import models, lookup

class MainPage(CommonHandler):
  def handle_get(self):

    template_values = {
        'self.user_settings': self.user_settings,
        'accounts': lookup.GetAllAccounts(self.user_settings),
        'transactions': lookup.GetAllTransactions(self.user_settings),
        'categories': lookup.GetAllCategories(self.user_settings)
    }

    self.write_to_template('templates/index.html', template_values)


class EditBudgetPage(CommonHandler):
  def handle_get(self):
    raw_budget_date = self.request.get('date')
    budget_date = datetime.datetime.now()
    if raw_budget_date:
      budget_date = datetime.datetime.strptime(raw_budget_date, '%m.%d.%Y')

    budget_key = ndb.Key(models.Budget, budget_date.strftime('%m.%Y'),
                         parent=self.user_settings.key)
    budget = budget_key.get()

    categories = lookup.GetAllCategories(self.user_settings)

    if budget:
      cat_id_to_planned_expense = dict(
          [(exp.category_id, exp.planned_value) for exp in budget.expenses])

      for category in categories:
        if category.key.id() in cat_id_to_planned_expense:
          category.planned_value = cat_id_to_planned_expense[
               category.key.id()]

    template_values = {
      'categories': categories,
      'budget_name': budget_date.strftime('%m.%Y'),
      'budget_date': budget_date.strftime('%m.%Y'),
      'budget': budget
    }

    self.write_to_template('templates/edit_budget.html', template_values)


class UserSettingsPage(CommonHandler):
  def handle_get(self):
    template_values = {
      'user_settings': self.user_settings
    }

    self.write_to_template('templates/user_settings.html', template_values)


class CreateUserPage(CommonHandler):
  def get(self):
    self.visitor = users.get_current_user()
    if not self.visitor:
      self.redirect(users.create_login_url(self.request.uri))
      return

    self.user_settings = lookup.GetUserSettings(self.visitor)
    if self.user_settings:
      self.redirect('/')

    self.write_to_template('templates/create_user.html', {})

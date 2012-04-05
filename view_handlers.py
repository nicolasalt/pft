import datetime
from google.appengine.api import users
from google.appengine.ext import ndb

from common_handlers import CommonHandler
from datastore import models, lookup

class MainPage(CommonHandler):
  def handle_get(self):

    template_values = {
        'profile': self.profile,
        'accounts': lookup.GetAllAccounts(self.profile),
        'transactions': lookup.GetAllTransactions(self.profile),
        'categories': lookup.GetAllCategories(self.profile)
    }

    self.write_to_template('templates/index.html', template_values)


class EditBudgetPage(CommonHandler):
  def handle_get(self):
    raw_budget_date = self.request.get('date')
    budget_date = datetime.datetime.now()
    if raw_budget_date:
      budget_date = datetime.datetime.strptime(raw_budget_date, '%m.%d.%Y')

    budget_key = ndb.Key(models.Budget, budget_date.strftime('%m.%Y'),
                         parent=self.profile.key)
    budget = budget_key.get()

    categories = lookup.GetAllCategories(self.profile)

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


class EditProfile(CommonHandler):
  def handle_get(self):
    self.write_to_template('templates/edit_profile.html', template_values)


class ManageProfilesPage(CommonHandler):
  def get(self):
    if self.init_user_and_profile(redirect_to_choose_profile=False):
      self.write_to_template('templates/manage_profiles.html', {})

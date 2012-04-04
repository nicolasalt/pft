import os
import datetime
from google.appengine.ext import ndb
import webapp2
import jinja2

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

    template_values = {
        'user_settings': user_settings,
        'accounts': lookup.GetAllAccounts(user_settings),
        'transactions': lookup.GetAllTransactions(user_settings),
        'categories': lookup.GetAllCategories(user_settings)
    }

    template = jinja_environment.get_template('templates/index.html')
    self.response.out.write(template.render(template_values))


class EditBudgetPage(webapp2.RequestHandler):
  def get(self):
    visitor = users.get_current_user()
    if not visitor:
      self.redirect(users.create_login_url(self.request.uri))

    user_settings = lookup.GetOrCreateUserSettings(visitor)

    raw_budget_date = self.request.get('date')
    budget_date = datetime.datetime.now()
    if raw_budget_date:
      budget_date = datetime.datetime.strptime(raw_budget_date, '%m.%d.%Y')

    budget_key = ndb.Key(models.Budget, budget_date.strftime('%m.%Y'),
                         parent=user_settings.key)
    budget = budget_key.get()

    categories = lookup.GetAllCategories(user_settings)

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

    template = jinja_environment.get_template('templates/edit_budget.html')
    self.response.out.write(template.render(template_values))

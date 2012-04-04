import os
import datetime
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
      budget_date = datetime.datetime.strptime(raw_budget_date, '%m/%d/%Y')

    template_values = {
      'categories': lookup.GetAllCategories(user_settings),
      'budget_name': budget_date.strftime('%m.%Y')
    }

    template = jinja_environment.get_template('templates/edit_budget.html')
    self.response.out.write(template.render(template_values))

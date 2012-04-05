import calendar
from datetime import datetime
from google.appengine.api import users
from google.appengine.ext import ndb

from common_handlers import CommonHandler
from datastore import models, lookup
import budget_util

class MainPage(CommonHandler):
  def HandleGet(self):

    template_values = {
        'profile': self.profile,
        'accounts': lookup.GetAllAccounts(self.profile),
        'transactions': lookup.GetAllTransactions(self.profile),
        'categories': lookup.GetAllCategories(self.profile)
    }

    self.WriteToTemplate('templates/index.html', template_values)


class EditBudgetPage(CommonHandler):
  def HandleGet(self):
    raw_budget_date = self.request.get('date')
    budget_date = datetime.now()
    if raw_budget_date:
      budget_date = datetime.strptime(raw_budget_date, '%m.%d.%Y')

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

    transactions = lookup.GetTransactionsForBudget(self.profile, budget)
    total_income, total_expenses = budget_util.CalculateExpensesAndIncome(
        budget, transactions)

    days = []
    _, days_in_current_month = calendar.monthrange(
        budget_date.year, budget_date.month)
    for day in xrange(days_in_current_month):
      days.append({
        'date': datetime(budget_date.year, budget_date.month, day + 1),
        'transactions': []
      })

    for transaction in transactions:
      days[transaction.date.day - 1]['transactions'].append(transaction)

    template_values = {
      'categories': categories,
      'budget_name': budget_date.strftime('%m.%Y'),
      'budget_date': budget_date.strftime('%m.%Y'),
      'budget': budget,
      'transactions': transactions,
      'days': days,
      'total_income': total_income,
      'total_expenses': total_expenses
    }

    self.WriteToTemplate('templates/edit_budget.html', template_values)


class EditProfile(CommonHandler):
  def HandleGet(self):
    self.WriteToTemplate('templates/edit_profile.html', template_values)


class ManageProfilesPage(CommonHandler):
  def get(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    template_values = {
      'profiles': lookup.GetAllProfiles(self.google_user),
    }

    self.WriteToTemplate('templates/manage_profiles.html', template_values)

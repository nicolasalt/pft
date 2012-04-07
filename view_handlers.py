import calendar
import csv
from datetime import datetime
from google.appengine.api import users
from google.appengine.ext import ndb

from common_handlers import CommonHandler
from datastore import models, lookup
import budget_util

class MainPage(CommonHandler):
  def HandleGet(self):

    template_values = {
      'accounts': lookup.GetAllAccounts(self.profile),
      'transactions': lookup.GetAllTransactions(self.profile),
      'categories': lookup.GetAllCategories(self.profile)
    }

    self.WriteToTemplate('templates/index.html', template_values)


class ImportFromFilePage(CommonHandler):
  def HandleGet(self):

    template_values = {
      'accounts': lookup.GetAllAccounts(self.profile),
      'imported_files': lookup.GetImportedFiles(self.profile, 10)
    }

    self.WriteToTemplate('templates/import_from_file.html', template_values)


class EditImportedFilePage(CommonHandler):
  def HandleGet(self):
    imported_file_id = int(self.request.get('id'))
    imported_file = lookup.GetImportedFileById(self.profile, imported_file_id)

    formatted_parsed_lines = []
    for row in csv.reader([imported_file.schema] +
                          imported_file.source_file.splitlines()):
      formatted_parsed_lines.append(row)


    template_values = {
      'imported_file': imported_file,
      'formatted_parsed_lines': formatted_parsed_lines[:13]
    }

    self.WriteToTemplate('templates/edit_imported_file.html', template_values)


class EditBudgetPage(CommonHandler):
  def HandleGet(self):
    raw_budget_date = self.request.get('date')
    budget_date = datetime.now()
    if raw_budget_date:
      budget_date = models.Budget.ParseDate(raw_budget_date)

    budget_key = ndb.Key(models.Budget, models.Budget.DateToStr(budget_date),
                         parent=self.profile.key)
    budget = budget_key.get()
    if not budget:
      budget = models.Budget(parent=self.profile.key, date=budget_date)

    categories = lookup.GetAllCategories(self.profile)
    id_to_cat = dict([(cat.key.id(), cat) for cat in categories])

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
      if (transaction.category_id is not None and
          transaction.category_id in id_to_cat):
        transaction.category = id_to_cat[transaction.category_id]
      days[transaction.date.day - 1]['transactions'].append(transaction)

    template_values = {
      'categories': categories,
      'budget': budget,
      'transactions': transactions,
      'days': days,
      'total_income': total_income,
      'total_expenses': total_expenses
    }

    self.WriteToTemplate('templates/edit_budget.html', template_values)


class EditProfile(CommonHandler):
  def HandleGet(self):
    self.WriteToTemplate('templates/edit_profile.html', {})


class ManageProfilesPage(CommonHandler):
  def get(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    template_values = {
      'profiles': lookup.GetAllProfiles(self.google_user),
    }

    self.WriteToTemplate('templates/manage_profiles.html', template_values)

import calendar
from datetime import datetime
from google.appengine.ext import ndb

from common_handlers import CommonHandler
from datastore import models, lookup
import budget_util
import parse_csv
from util import ndb_json


class MainPage(CommonHandler):
  def HandleGet(self):
    budget = budget_util.GetBudget(self.profile, self.request.get('date'))

    transactions = lookup.GetTransactionsForBudget(self.profile, budget)
    unplanned_income, unplanned_expenses = (
        budget_util.CalculateUnplannedExpensesAndIncome(
            budget, transactions))

    total_balance = sum([a.balance for a in self.profile.accounts])
    categories_total_balance = sum([c.balance for c in self.profile.categories])

    budget_view_items = []
    common_savings = 9000
    max_expense = 0
    for item in budget.items:
      if item.category_id is not None:
        budget_view_items.append({
          'name': self.profile.categories[item.category_id].name,
          'amount': item.planned_amount
        })
        common_savings -= item.planned_amount
        max_expense = max(max_expense, item.planned_amount)

    budget_view_items.append({
      'name': 'Other expenses',
      'amount': unplanned_expenses
    })
    common_savings -= unplanned_expenses
    max_expense = max(max_expense, item.planned_amount)

    template_values = {
      'total_balance': total_balance,
      'categories_total_balance': categories_total_balance,
      'budget_items': budget_view_items,
      'common_savings': common_savings,
      'max_expense': max_expense
    }

    self.WriteToTemplate('templates/index.html', template_values)


class AdminPage(CommonHandler):
  def HandleGet(self):

    template_values = {
      'transactions': lookup.GetAllTransactions(self.profile)
    }

    self.WriteToTemplate('templates/admin.html', template_values)


class ImportFromFilePage(CommonHandler):
  def HandleGet(self):

    template_values = {
      'imported_file_descriptions':
          lookup.GetOrCreateImportedFileList(self.profile).imported_files
    }

    self.WriteToTemplate('templates/import_from_file.html', template_values)


class EditImportedFilePage(CommonHandler):
  def HandleGet(self):
    imported_file_id = int(self.request.get('id'))
    imported_file = lookup.GetImportedFileById(self.profile, imported_file_id)

    template_values = {
      'imported_file': imported_file,
      'imported_transactions_json': [
          ndb_json.encode(t) for t in imported_file.parsed_transactions],
      'account': lookup.GetAccountById(self.profile, imported_file.account_id)
    }
    if imported_file.source_file:
      source_file_lines = imported_file.source_file.splitlines()
      if imported_file.schema:
        source_file_lines = [imported_file.schema] + source_file_lines
      template_values['formatted_parsed_lines'] = parse_csv.ParseCsvToPreview(
          source_file_lines)[:13]

    self.WriteToTemplate('templates/edit_imported_file.html', template_values)


class EditBudgetPage(CommonHandler):
  def HandleGet(self):
    budget = budget_util.GetBudget(self.profile, self.request.get('date'))

    transactions = lookup.GetTransactionsForBudget(self.profile, budget)
    unplanned_income, unplanned_expenses = (
        budget_util.CalculateUnplannedExpensesAndIncome(
            budget, transactions))

    template_values = {
      'budget': budget,
      'unplanned_income': unplanned_income,
      'unplanned_expenses': unplanned_expenses
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


class DetailedExpensesPage(CommonHandler):
  def HandleGet(self):
    """
      This page allow to view filtered transactions.
      Possible filters:
       - for a budget month
       - for a category (not implemented)
       - for an account (not implemented)
    """
    raw_budget_date = self.request.get('date')
    budget_date = datetime.now()
    if raw_budget_date:
      budget_date = models.Budget.ParseDate(raw_budget_date)

    budget_key = ndb.Key(models.Budget, models.Budget.DateToStr(budget_date),
                         parent=self.profile.key)
    budget = budget_key.get()
    if not budget:
      budget = models.Budget(parent=self.profile.key, date=budget_date)

    id_to_cat = dict([(id, cat) for id, cat in enumerate(
      self.profile.categories)])

    id_to_account = dict([(id, acc) for id, acc in enumerate(
        self.profile.accounts)])

    transactions = lookup.GetTransactionsForBudget(self.profile, budget)

    total_income = 0
    total_expenses = 0
    for transaction in transactions:
      if transaction.amount > 0:
        total_expenses += transaction.amount
      else:
        total_income -= transaction.amount


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
      transaction.account = id_to_account[transaction.account_id]
      days[transaction.date.day - 1]['transactions'].append(transaction)

    template_values = {
      'budget': budget,
      'transactions': transactions,
      'transactions_json': [ndb_json.encode(t) for t in transactions],
      'days': days,
      'total_income': total_income,
      'total_expenses': total_expenses
    }

    self.WriteToTemplate('templates/detailed_expenses.html', template_values)

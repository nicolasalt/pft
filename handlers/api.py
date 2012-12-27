from google.appengine.api import users
from common import CommonHandler
from datastore import lookup
from util import ndb_json, budget_util, parse, parse_csv

class GetProfile(CommonHandler):
  def HandleGet(self):
    response = {
      'visitor': self.visitor,
      'logout_url': users.create_logout_url(self.request.uri),
      'profile': self.profile
    }
    if self.profile:
      for i, category in enumerate(self.profile.categories):
        category.category_id = i
      for i, account in enumerate(self.profile.accounts):
        account.account_id = i

      response.update({
        'user_profile_settings': lookup.GetOrCreateUserProfileSettings(
            self.profile, self.visitor),
        'total_balance': self.GetTotalAccountBalance(),
        'categories_total_balance':
            sum([c.balance for c in self.profile.categories]),
      })

    self.WriteToJson(response)


class GetBudget(CommonHandler):
  def HandleGet(self):
    budget = budget_util.GetBudget(self.profile, self.request.get('date'))

    transactions = lookup.GetTransactionsForBudget(self.profile, budget)
    unplanned_income, unplanned_expenses = (
        budget_util.CalculateUnplannedExpensesAndIncome(
            budget, transactions))

    categories_total_balance = sum([c.balance for c in self.profile.categories])

    budget_view_items = budget_util.GetBudgetViewItems(self.profile, budget)
    common_savings = 9000
    max_expense = 0
    for item in budget.items:
      if item.category_id is not None:
        common_savings -= item.planned_amount
        max_expense = max(max_expense, item.planned_amount)

    budget_view_items.append({
      'name': 'Other expenses',
      'amount': unplanned_expenses
    })
    common_savings -= unplanned_expenses
    max_expense = max(max_expense, common_savings)

    response = {
      'total_balance': self.GetTotalAccountBalance(),
      'budget': budget,
      'categories_total_balance': categories_total_balance,
      'budget_items': budget_view_items,
      'common_savings': common_savings,
      'max_expense': max_expense
    }

    self.WriteToJson(response)


class GetTransactions(CommonHandler):
  def HandleGet(self):
    """
      This page allows to view filtered transactions.
      Possible filters:
       - for a budget month
       - for a category
       - for an account
    """
    category_id = parse.ParseInt(self.request.get('category_id'))
    account_id = parse.ParseInt(self.request.get('account_id'))
    budget_date = self.request.get('budget_date')

    budget = None
    account = None
    category = None
    # TODO: fill this info in js
    if category_id is not None or account_id is not None:
      if category_id is not None:
        category = self.profile.categories[category_id]
      if account_id is not None:
        account = self.profile.accounts[account_id]
      transactions = lookup.GetTransactions(
          self.profile, category_id=category_id, account_id=account_id)
    else:
      budget = budget_util.GetBudget(self.profile, budget_date)
      transactions = lookup.GetTransactionsForBudget(self.profile, budget)

    for transaction in transactions:
      if transaction.category_id is not None:
        transaction.category =  self.profile.categories[transaction.category_id]
      if transaction.account_id is not None:
        transaction.account = self.profile.accounts[transaction.account_id]

    response = {
      'budget': budget,
      'next_month': budget.GetNextBudgetDate() if budget else None,
      'previous_month': budget.GetPreviousBudgetDate() if budget else None,
      'category': category,
      'account': account,
      'transactions': transactions
    }

    self.WriteToJson(response)


class GetImportedFileDescriptions(CommonHandler):
  def HandleGet(self):

    response = {
      'imported_file_descriptions':
          lookup.GetOrCreateImportedFileList(self.profile).imported_files
    }

    self.WriteToJson(response)


class GetImportedFile(CommonHandler):
  def HandleGet(self):
    imported_file_id = int(self.request.get('id'))
    imported_file = lookup.GetImportedFileById(self.profile, imported_file_id)

    response = {
      'imported_file': imported_file
    }
    if imported_file.source_file:
      source_file_lines = imported_file.source_file.splitlines()
      if imported_file.schema:
        source_file_lines = [imported_file.schema] + source_file_lines
      response['formatted_parsed_lines'] = parse_csv.ParseCsvToPreview(
          source_file_lines)[:13]

    self.WriteToJson(response)

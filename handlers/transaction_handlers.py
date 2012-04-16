from datetime import datetime

from common import CommonHandler
from datastore import models, update, lookup
import datastore.lookup
from util import parse, budget_util, ndb_json
import util.budget_util
import util.ndb_json
import util.parse


class DoEditTransaction(CommonHandler):
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

    if (not description and
        account_id is not None and dest_account_id is not None):
      description = 'Transfer from "%s" account to "%s" account' % (
          self.profile.accounts[account_id].name,
          self.profile.accounts[dest_account_id].name)

    source = 'budget' if budget_date else 'manual'

    if transaction_id is not None:
      update.UpdateTransaction(
          self.profile, transaction_id, amount, date, account_id=account_id,
          category_id=category_id, description=description,
          dest_category_id=dest_category_id, dest_account_id=dest_account_id,
          source=source)
    else:
      update.AddTransaction(
          self.profile, amount, date, account_id=account_id,
          category_id=category_id, description=description,
          dest_category_id=dest_category_id, dest_account_id=dest_account_id,
          source=source)

    self.response.set_status(200)


# Pages


class TransactionReportPage(CommonHandler):
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

    template_values = {
      'budget': budget,
      'next_month': budget.GetNextBudgetDate() if budget else None,
      'previous_month': budget.GetPreviousBudgetDate() if budget else None,
      'category': category,
      'account': account,
      'transactions': transactions,
      'transactions_json': [ndb_json.encode(t) for t in transactions]
    }

    self.WriteToTemplate('templates/transactions/transaction_report.html', template_values)

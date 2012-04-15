from datetime import datetime

from common import CommonHandler
from datastore import models, update
from util import parse


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

from google.appengine.ext import ndb
from datastore import models


def _UpdateTransactionRelations(profile, transaction, amount):
  """
    Does not update transaction.amount.

    Args:
      amount: To add transaction: transaction.amount.
         To delete transaction: -transaction.amount.
         To modify transaction: new_amount - transaction.amount.
  """
  if transaction.account_id is not None:
    account = profile.GetAccountById(transaction.account_id)
    account.balance -= amount

  if transaction.category_id is not None:
    category = profile.GetCategoryById(transaction.category_id)
    category.balance -= amount

  if transaction.dest_account_id is not None:
    dest_account = profile.GetAccountById(transaction.dest_account_id)
    dest_account.balance += amount

  if transaction.dest_category_id is not None:
    dest_category = profile.GetAccountById(profile, transaction.dest_category_id)
    dest_category.balance += amount

  profile.put()


@ndb.transactional
def AddTransaction(profile, amount, date, account_id=None, category_id=None,
                   description=None, dest_account_id=None,
                   dest_category_id=None, source='unknown'):
  transaction = models.Transaction(
    parent=profile.key,
    account_id=account_id,
    amount=amount,
    date=date,
    description=description,
    category_id=category_id,
    dest_account_id=dest_account_id,
    dest_category_id=dest_category_id,
    source=source)

  # reload the latest profile
  profile = models.Profile.get_by_id(profile.key.id())
  _UpdateTransactionRelations(profile, transaction, amount)

  transaction.put()
  return transaction


@ndb.transactional
def UpdateTransaction(profile, transaction_id, amount, date, account_id=None,
                      category_id=None, description=None, dest_account_id=None,
                      dest_category_id=None, source='unknown'):
  transaction = models.Transaction.Get(profile, transaction_id)

  # reload the latest profile
  profile = models.Profile.get_by_id(profile.key.id())
  _UpdateTransactionRelations(profile, transaction, -transaction.amount)

  transaction.account_id = account_id
  transaction.amount = amount
  transaction.date = date
  transaction.description = description
  transaction.category_id = category_id
  transaction.dest_account_id = dest_account_id
  transaction.dest_category_id = dest_category_id
  transaction.source = source

  _UpdateTransactionRelations(profile, transaction, amount)

  transaction.put()
  return transaction


@ndb.transactional
def DeleteTransactions(profile, transaction_ids):
  keys = []
  for transaction_id in transaction_ids:
    keys.append(ndb.Key(models.Transaction, transaction_id, parent=profile.key))
  transactions = ndb.get_multi(keys)

  # reload the latest profile
  profile = models.Profile.get_by_id(profile.key.id())
  for transaction in transactions:
    _UpdateTransactionRelations(profile, transaction, -transaction.amount)

  ndb.delete_multi(keys)

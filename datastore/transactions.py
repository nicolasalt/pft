from google.appengine.ext import ndb
from datastore import models
from util import currency_rates_util


def _UpdateTransactionRelations(profile, transaction, amount):
  """
    Does not update transaction.amount.

    Args:
      amount: To add transaction: transaction.amount.
         To delete transaction: -transaction.amount.
         To modify transaction: new_amount - transaction.amount.
  """
  if transaction.dest_account_id is not None:
    dest_account = profile.GetAccountById(transaction.dest_account_id)

    if transaction.source_account_id is not None:
      source_account = profile.GetAccountById(transaction.source_account_id)
      source_account.balance -= amount
      amount = currency_rates_util.ConvertCurrency(
        amount, source_account.currency, dest_account.currency)

    dest_account.balance += amount

  else:
    raise ValueError('dest_account_id must be specified')


# TODO: don't use cross-group transactions, cache currency rates in advance.
@ndb.transactional(xg=True)
def AddTransaction(profile_id, amount, date, source_account_id=None,
                   description=None, dest_account_id=None, source=None):
  transaction = models.Transaction(
    parent=ndb.Key(models.Profile, profile_id),
    source_account_id=source_account_id,
    amount=amount,
    date=date,
    description=description,
    dest_account_id=dest_account_id,
    source=source)

  profile = models.Profile.get_by_id(profile_id)
  _UpdateTransactionRelations(profile, transaction, amount)

  profile.put()
  transaction.put()
  return transaction


@ndb.transactional(xg=True)
def UpdateTransaction(profile_id, transaction_id, amount, date, description=None):
  transaction = models.Transaction.Get(profile_id, transaction_id)

  profile = models.Profile.get_by_id(profile_id)
  _UpdateTransactionRelations(profile, transaction, -transaction.amount)
  _UpdateTransactionRelations(profile, transaction, amount)

  transaction.amount = amount
  transaction.date = date
  transaction.description = description

  profile.put()
  transaction.put()
  return transaction


@ndb.transactional(xg=True)
def DeleteTransactions(profile_id, transaction_ids):
  keys = []
  for transaction_id in transaction_ids:
    keys.append(ndb.Key(models.Transaction, transaction_id,
      parent=ndb.Key(models.Profile, profile_id)))
  transactions = ndb.get_multi(keys)

  profile = models.Profile.get_by_id(profile_id)
  for transaction in transactions:
    _UpdateTransactionRelations(profile, transaction, -transaction.amount)

  profile.put()
  ndb.delete_multi(keys)

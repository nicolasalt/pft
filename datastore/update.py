from google.appengine.ext import ndb
from datastore import models, lookup


def AddAccount(profile, name, currency):
  account = models.Account(
      parent=profile.key, name=name, currency= currency)
  account.put()
  return account


def _UpdateTransactionRelations(profile, transaction, amount):
  """
    Does not update transaction.amount.

    Args:
      amount: To add transaction: transaction.amount.
         To delete transaction: -transaction.amount.
         To modify transaction: new_amount - transaction.amount.
  """
  account = lookup.GetAccountById(profile, transaction.account_id)
  account.balance -= amount
  account.put()

  if transaction.category_id:
    category = lookup.GetCategoryById(profile, transaction.category_id)
    category.balance -= amount
    category.put()

  if transaction.dest_account_id is not None:
    dest_account = lookup.GetAccountById(profile, transaction.dest_account_id)
    dest_account.balance += amount
    dest_account.put()

  if transaction.dest_category_id is not None:
    transaction.dest_category_id = transaction.dest_category_id
    dest_category = lookup.GetCategoryById(profile, transaction.dest_category_id)
    dest_category.balance += amount
    dest_category.put()

# TODO: make 'transaction' module
@ndb.transactional
def AddTransaction(profile, account_id, amount, date, category_id,
                   description, dest_account_id=None, dest_category_id=None):
  transaction = models.Transaction(
    parent=profile.key,
    account_id=account_id,
    amount=amount,
    date=date,
    description=description)

  if category_id:
    transaction.category_id = category_id
  if dest_account_id is not None:
    transaction.dest_account_id = dest_account_id
  if dest_category_id is not None:
    transaction.dest_category_id = dest_category_id

  _UpdateTransactionRelations(profile, transaction, amount)

  transaction.put()
  return transaction


def UpdateProfile(profile, **kw):
  for key, value in kw.iteritems():
    setattr(profile, key, value)
  profile.put()


def AddProfile(owner, name, **kw):
  if 'name' in kw or 'owner' in kw:
    raise AttributeError('kw must not contain name or owner.')

  profile = models.Profile(name=name, owner=owner)
  for key, value in kw.iteritems():
    setattr(profile, key, value)
  profile.users.append(owner)

  profile.put()
  return profile


def AddUserToProfile(profile, google_user):
  profile.users.append(google_user)
  profile.put()


def UpdateUser(user, **kw):
  for key, value in kw.iteritems():
    setattr(user, key, value)
  user.put()


@ndb.transactional
def DeleteTransactions(profile, transaction_ids):
  keys = []
  for transaction_id in transaction_ids:
    keys.append(ndb.Key(models.Transaction, transaction_id, parent=profile.key))
  transactions = ndb.get_multi(keys)

  for transaction in transactions:
    _UpdateTransactionRelations(profile, transaction, -transaction.amount)

  ndb.delete_multi(keys)

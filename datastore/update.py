from datetime import datetime
from google.appengine.ext import ndb
from datastore import models, lookup


def AddAccount(profile, name, currency):
  account = models.Account(name=name, currency=currency)
  profile.accounts.append(account)
  profile.put()
  return account


def EditAccount(profile, account_id, name, currency):
  profile.accounts[account_id].name = name
  profile.accounts[account_id].currency = currency
  profile.put()
  return profile.accounts[account_id]


def AddCategory(profile, name):
  category = models.Category(name=name)
  profile.categories.append(category)
  profile.put()
  return category


def EditCategory(profile, category_id, name):
  profile.categories[category_id].name = name
  profile.put()
  return profile.categories[category_id]


def _UpdateTransactionRelations(profile, transaction, amount):
  """
    Does not update transaction.amount.

    Args:
      amount: To add transaction: transaction.amount.
         To delete transaction: -transaction.amount.
         To modify transaction: new_amount - transaction.amount.
  """
  if transaction.account_id is not None:
    account = lookup.GetAccountById(profile, transaction.account_id)
    account.balance -= amount

  if transaction.category_id is not None:
    category = lookup.GetCategoryById(profile, transaction.category_id)
    category.balance -= amount

  if transaction.dest_account_id is not None:
    dest_account = lookup.GetAccountById(profile, transaction.dest_account_id)
    dest_account.balance += amount

  if transaction.dest_category_id is not None:
    dest_category = lookup.GetCategoryById(profile,
                                           transaction.dest_category_id)
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
  profile = lookup.GetProfileById(profile.key.id())
  _UpdateTransactionRelations(profile, transaction, amount)

  transaction.put()
  return transaction


@ndb.transactional
def UpdateTransaction(profile, transaction_id, amount, date, account_id=None,
                      category_id=None, description=None, dest_account_id=None,
                      dest_category_id=None, source='unknown'):
  transaction = lookup.GetTransactionById(profile, transaction_id)

  # reload the latest profile
  profile = lookup.GetProfileById(profile.key.id())
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
  profile = lookup.GetProfileById(profile.key.id())
  for transaction in transactions:
    _UpdateTransactionRelations(profile, transaction, -transaction.amount)

  ndb.delete_multi(keys)


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


def UpdateCurrencyRates(new_rates):
  """
    Args:
      new rates: dict like {'euro': 1.34, 'rub': 0.33}
  """
  ratesModel = lookup.GetLatestCurrencyRates()
  rates = dict([(r.currency, r.rate) for r in ratesModel.rates])
  rates.update(new_rates)
  ratesModel.rates = [models.CurrencyRates.Rate(currency=c, rate=r)
                      for c, r in rates.iteritems()]
  ratesModel.last_updated = datetime.now()
  ratesModel.put()

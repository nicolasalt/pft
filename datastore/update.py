from google.appengine.ext import ndb
from datastore import models, lookup


def AddAccount(profile, name, currency):
  account = models.Account(
      parent=profile.key, name=name, currency= currency)
  account.put()
  return account


# TODO: make 'transaction' module
@ndb.transactional
def AddTransaction(profile, account_id, amount, date, category_id,
                   description, dest_account_id=None, dest_category_id=None):
  account = lookup.GetAccountById(profile, account_id)
  transaction = models.Transaction(
    parent=profile.key,
    account_id=account.key.id(),
    amount=amount,
    date=date,
    description=description)

  account.balance -= amount
  account.put()

  if category_id:
    transaction.category_id = category_id
    category = lookup.GetCategoryById(profile, category_id)
    category.balance -= amount
    category.put()

  if dest_account_id is not None:
    transaction.dest_account_id = dest_account_id
    dest_account = lookup.GetAccountById(profile, account_id)
    dest_account.balance += amount
    dest_account.put()

  if dest_category_id is not None:
    transaction.dest_category_id = dest_category_id
    dest_category = lookup.GetCategoryById(profile, dest_category_id)
    dest_category.balance -= amount
    dest_category.put()

  transaction.put()


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

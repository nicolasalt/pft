from google.appengine.ext import ndb
from datastore import models, lookup


def AddAccount(profile, name, currency):
  account = models.Account(
      parent=profile.key, name=name, currency= currency)
  account.put()
  return account


@ndb.transactional
def AddTransaction(profile, account_id, amount, date, category_id):
  account = models.Account.get_by_id(account_id, parent=profile.key)
  transaction = models.Transaction(
    parent=profile.key,
    account_id=account.key.id(),
    amount=amount,
    date=date)
  if category_id:
    transaction.category_id = category_id
    category = models.Category.get_by_id(category_id, parent=profile.key)
    category.balance -= amount
    category.put()
  transaction.put()
  account.balance -= amount
  account.put()


def UpdateProfile(profile, **kw):
  for key, value in kw.iteritems():
    profile[key] = value
  profile.put()


def AddProfile(owner, name, **kw):
  if 'name' in kw or owner in kw:
    raise AttributeError('kw must not contain name or owner.')

  profile = models.Profile(name=name, owner=owner)
  for key, value in kw.iteritems():
    profile[key] = value
  profile.users.append(owner)

  profile.put()
  return profile


def AddUserToProfile(profile, google_user):
  profile.users.append(google_user)
  profile.put()


def UpdateUser(user, **kw):
  for key, value in kw.iteritems():
    user[key] = value
  user.put()

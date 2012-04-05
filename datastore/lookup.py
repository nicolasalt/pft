from google.appengine.ext import ndb
from datastore import models


def GetUser(google_user):
  user = models.User.MakeKey(google_user.user_id()).get()
  if not user:
    user = models.User(google_user=google_user)
  return user


def GetActiveProfile(google_user):
  profile_id = GetUser(google_user).active_profile_id
  if profile_id:
    return GetProfileById(profile_id)
  else:
    return None


def GetAllProfiles(google_user):
  return models.Profile.query().filter(
      models.Profile.users == google_user).fetch(100)


def GetProfileByCode(code):
  return ndb.Key(urlsafe=code).get()


def GetProfileById(profile_id):
  return ndb.Key(models.Profile, profile_id).get()


def GetAllAccounts(user_settings):
  account_query = models.Account.query(
    ancestor=user_settings.key).order(-models.Account.date)
  return account_query.fetch(1000)


def GetAllTransactions(user_settings):
  transaction_query = models.Transaction.query(
    ancestor=user_settings.key).order(-models.Transaction.date)
  return transaction_query.fetch(1000)


def GetAllCategories(user_settings):
  category_query = models.Category.query(
    ancestor=user_settings.key).order(-models.Category.name)
  return category_query.fetch(1000)


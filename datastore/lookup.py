from datetime import timedelta, time
from datetime import datetime
from google.appengine.ext import ndb
from datastore import models


def GetUser(google_user):
  user = models.User.MakeKey(google_user.user_id()).get()
  if not user:
    user = models.User(id=google_user.user_id(), google_user=google_user)
  return user


def GetActiveProfile(google_user):
  profile_id = GetUser(google_user).active_profile_id
  if profile_id:
    return GetProfileById(profile_id)
  else:
    return None


def GetOrCreateUserProfileSettings(profile, visitor):
  settings = None
  for s in visitor.profile_settings:
    if s.profile_id == profile.key.id():
      settings = s
  if settings is None:
    settings = models.UserProfileSettings(profile_id=profile.key.id())
    visitor.profile_settings.append(settings)

  return settings


def GetAllProfiles(google_user):
  return models.Profile.query().filter(
    models.Profile.users == google_user).fetch(100)


def GetProfileByCode(code):
  return ndb.Key(urlsafe=code).get()


def GetProfileById(profile_id):
  return ndb.Key(models.Profile, profile_id).get()


def GetAllTransactions(profile):
  transaction_query = models.Transaction.query(
    ancestor=profile.key).order(-models.Transaction.date)
  return transaction_query.fetch(1000)


def GetTransactionsForBudget(profile, budget):
  start_date, end_date = budget.GetDateRange()
  return models.Transaction.query(ancestor=profile.key).filter(
    models.Transaction.date >= start_date,
    models.Transaction.date < end_date).fetch(1000)


def GetTransactions(profile, category_id, account_id):
  query = models.Transaction.query(ancestor=profile.key)
  if category_id is not None:
    query = query.filter(ndb.query.OR(
      models.Transaction.source_category_id == category_id,
      models.Transaction.dest_category_id == category_id))
  if account_id is not None:
    query = query.filter(ndb.query.OR(
      models.Transaction.source_account_id == account_id,
      models.Transaction.dest_account_id == account_id))
  return query.fetch(1000)


def GetTransactionById(profile, transaction_id):
  return models.Transaction.get_by_id(transaction_id, parent=profile.key)


def GetAccountById(profile, account_id):
  assert 0 <= account_id < len(profile.accounts)
  # TODO: How to delete accounts?
  return profile.accounts[account_id]


def GetCategoryById(profile, category_id):
  assert 0 <= category_id < len(profile.categories)
  # TODO: How to delete categories?
  return profile.categories[category_id]


def GetImportedFileById(profile, imported_file_id):
  return models.ImportedFile.get_by_id(imported_file_id, parent=profile.key)


def GetOrCreateImportedFileList(profile):
  imported_file_list = models.ImportedFileList.get_by_id(
    'imported_file_list', parent=profile.key)
  if not imported_file_list:
    imported_file_list = models.ImportedFileList(
      id='imported_file_list', parent=profile.key)
  return imported_file_list


def GetTransactionsForDay(profile, date, account_id):
  beginning_of_day = datetime.combine(date.date(), time(0))
  query = (models.Transaction.
           query(ancestor=profile.key).
           filter(models.Transaction.date >= beginning_of_day).
           filter(models.Transaction.date < beginning_of_day + timedelta(days=1)).
           order(-models.Transaction.date))
  if account_id:
    query.filter(models.Transaction.source_account_id == account_id)
  return query.fetch(1000)


def GetLatestCurrencyRates():
  return models.CurrencyRates.get_or_insert('global_currency_rates')

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


def GetAllProfiles(google_user):
  return models.Profile.query().filter(
      models.Profile.users == google_user).fetch(100)


def GetProfileByCode(code):
  return ndb.Key(urlsafe=code).get()


def GetProfileById(profile_id):
  return ndb.Key(models.Profile, profile_id).get()


def GetAllAccounts(profile):
  account_query = models.Account.query(
    ancestor=profile.key).order(-models.Account.date)
  return account_query.fetch(1000)


def GetAllTransactions(profile):
  transaction_query = models.Transaction.query(
    ancestor=profile.key).order(-models.Transaction.date)
  return transaction_query.fetch(1000)


def GetAllCategories(profile):
  category_query = models.Category.query(
    ancestor=profile.key).order(-models.Category.name)
  return category_query.fetch(1000)


def GetTransactionsForBudget(profile, budget):
  start_date, end_date = budget.GetDateRange()
  return models.Transaction.query(ancestor=profile.key).filter(
      models.Transaction.date >= start_date,
      models.Transaction.date < end_date).fetch(1000)


def GetAccountById(profile, account_id):
  return models.Account.get_by_id(account_id, parent=profile.key)


def GetCategoryById(profile, category_id):
  return models.Category.get_by_id(category_id, parent=profile.key)


def GetImportedFileById(profile, imported_file_id):
  return models.ImportedFile.get_by_id(imported_file_id, parent=profile.key)


def GetOrCreateImportedFileList(profile):
  imported_file_list = models.ImportedFileList.get_by_id(
      'imported_file_list', parent=profile.key)
  if not imported_file_list:
    imported_file_list = models.ImportedFileList(
        id='imported_file_list', parent=profile.key)
  return imported_file_list

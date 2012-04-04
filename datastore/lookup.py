from datastore import models


def GetOrCreateUserSettings(user):
  key = models.UserSettings.MakeKey(user.user_id())
  return models.UserSettings.get_or_insert(key.id(), user=user)


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


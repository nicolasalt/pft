from datastore import models


def GetUserSettings(user):
  results = models.UserSettings.query().filter(
      models.UserSettings.users == user).fetch(1)
  if results and len(results) > 0:
    return results[0]
#  return models.UserSettings.MakeKey(user.user_id()).get()


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



def ConvertDatetime(date):
  return date.isoformat()


def ConvertAccountToDict(account):
  return {
    'balance': account.balance,
    'creation_time': ConvertDatetime(account.creation_time),
    'currency': account.currency,
    'id': account.id,
    'name': account.name
  }


def ConvertCategoryToDict(category):
  return {
    'balance': category.balance,
    'creation_time': ConvertDatetime(category.creation_time),
    'id': category.id,
    'name': category.name
  }


def ConvertProfileToDict(profile):
  return {
    'accounts': [ConvertAccountToDict(c) for c in profile.accounts],
    'categories': [ConvertCategoryToDict(c) for c in profile.categories],
    'creation_time': ConvertDatetime(profile.creation_time),
    'id': profile.key.id(),
    'main_currency': profile.main_currency,
    'name': profile.name
  }


def ConvertUserProfileSettingsToDict(profile_settings):
  return {
    'cash_account_id': profile_settings.cash_account_id,
    'important_account_ids': profile_settings.important_account_ids,
    'main_account_id': profile_settings.main_account_id
  }

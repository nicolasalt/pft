def ConvertDatetime(date):
  return date.isoformat()


def ConvertAccount(account):
  return {
    'balance': account.balance,
    'creation_time': ConvertDatetime(account.creation_time),
    'currency': account.currency,
    'id': account.id,
    'name': account.name
  }


def ConvertCategory(category):
  return {
    'balance': category.balance,
    'creation_time': ConvertDatetime(category.creation_time),
    'id': category.id,
    'name': category.name
  }


def ConvertProfile(profile):
  return {
    'accounts': [ConvertAccount(c) for c in profile.accounts],
    'categories': [ConvertCategory(c) for c in profile.categories],
    'creation_time': ConvertDatetime(profile.creation_time),
    'id': profile.key.id(),
    'main_currency': profile.main_currency,
    'name': profile.name,
    'profile_code': profile.key.urlsafe()
  }


def ConvertUserProfileSettings(profile_settings):
  return {
    'cash_account_id': profile_settings.cash_account_id,
    'important_account_ids': profile_settings.important_account_ids,
    'main_account_id': profile_settings.main_account_id
  }


def ConvertTransaction(transaction):
  return {
    'amount': transaction.amount,
    'date': ConvertDatetime(transaction.date),
    'description': transaction.description,
    'source_account_id': transaction.source_account_id,
    'dest_account_id': transaction.dest_account_id,
    'source_category_id': transaction.source_category_id,
    'dest_category_id': transaction.dest_category_id,
    'source': transaction.source,
  }

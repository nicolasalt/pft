def ConvertDatetime(date):
  return date.isoformat()


def ConvertAccount(account):
  return {
    'balance': account.balance,
    'creation_time': ConvertDatetime(account.creation_time),
    'currency': account.currency,
    'id': account.id,
    'name': account.name,
    'type': account.type
  }


def ConvertProfile(profile):
  return {
    'accounts': [ConvertAccount(c) for c in profile.accounts],
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
    'id': transaction.key.id(),
    'amount': transaction.amount,
    'date': ConvertDatetime(transaction.date),
    'description': transaction.description,
    'source_account_id': transaction.source_account_id,
    'dest_account_id': transaction.dest_account_id,
    'source': transaction.source,
  }

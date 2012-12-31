import common
import converters
from datastore import lookup, models
from util import  budget_util, parse, parse_csv, currency_rates_util


class GetActiveProfile(common.CommonHandler):
  @common.active_profile_required
  def HandleGet(self):
    return {
      'active_profile': converters.ConvertProfileToDict(self.profile),
      'user_profile_settings': converters.ConvertUserProfileSettingsToDict(
        self.visitor.GetOrCreateProfileSettings(self.profile.key.id())),
      'total_balance': self.GetTotalAccountBalance(),
    }

  def GetTotalAccountBalance(self):
    total = currency_rates_util.CalculateCurrencySum(
      [(a.balance, a.currency) for a in self.profile.accounts],
      self.profile.main_currency)
    return total or 0


class GetProfiles(common.CommonHandler):
  def HandleGet(self):
    return {
      'profiles': [converters.ConvertProfileToDict(p)
                   for p in models.Profile.GetAllForUser(self.visitor.key.id())],
    }


# Not tested


class GetTransactions(common.CommonHandler):
  def HandleGet(self):
    """
      This page allows to view filtered transactions.
      Possible filters:
       - for a budget month
       - for a category
       - for an account
    """
    category_id = parse.ParseInt(self.request.get('category_id'))
    account_id = parse.ParseInt(self.request.get('account_id'))
    budget_date = self.request.get('budget_date')

    budget = None
    account = None
    category = None
    # TODO: fill this info in js
    if category_id is not None or account_id is not None:
      if category_id is not None:
        category = self.profile.categories[category_id]
      if account_id is not None:
        account = self.profile.accounts[account_id]
      transactions = lookup.GetTransactions(
        self.profile, category_id=category_id, account_id=account_id)
    else:
      budget = budget_util.GetBudget(self.profile, budget_date)
      transactions = lookup.GetTransactionsForBudget(self.profile, budget)

    for transaction in transactions:
      if transaction.category_id is not None:
        transaction.category = self.profile.categories[transaction.category_id]
      if transaction.account_id is not None:
        transaction.account = self.profile.accounts[transaction.account_id]

    response = {
      'budget': budget,
      'next_month': budget.GetNextBudgetDate() if budget else None,
      'previous_month': budget.GetPreviousBudgetDate() if budget else None,
      'category': category,
      'account': account,
      'transactions': transactions
    }

    self.WriteToJson(response)


class GetImportedFileDescriptions(common.CommonHandler):
  def HandleGet(self):
    response = {
      'imported_file_descriptions':
        lookup.GetOrCreateImportedFileList(self.profile).imported_files
    }

    self.WriteToJson(response)


class GetImportedFile(common.CommonHandler):
  def HandleGet(self):
    imported_file_id = int(self.request.get('id'))
    imported_file = lookup.GetImportedFileById(self.profile, imported_file_id)

    response = {
      'imported_file': imported_file
    }
    if imported_file.source_file:
      source_file_lines = imported_file.source_file.splitlines()
      if imported_file.schema:
        source_file_lines = [imported_file.schema] + source_file_lines
      response['formatted_parsed_lines'] = parse_csv.ParseCsvToPreview(
        source_file_lines)[:13]

    self.WriteToJson(response)

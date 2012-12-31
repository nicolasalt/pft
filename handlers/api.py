import common
import converters
from datastore import lookup, models
from util import   parse, parse_csv, currency_rates_util


class GetActiveProfile(common.CommonHandler):
  @common.active_profile_required
  def HandleGet(self):
    return {
      'active_profile': converters.ConvertProfile(self.profile),
      'user_profile_settings': converters.ConvertUserProfileSettings(
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
      'profiles': [converters.ConvertProfile(p)
                   for p in models.Profile.GetAllForUser(self.visitor.key.id())],
    }


class GetTransactions(common.CommonHandler):
  @common.active_profile_required
  def HandleGet(self):
    """
      This page allows to view filtered transactions.
      Possible filters:
       - for a category
       - for an account
    """
    # TODO: add sort options
    category_id = parse.ParseInt(self.request.get('category_id'))
    account_id = parse.ParseInt(self.request.get('account_id'))

    transactions = models.Transaction.GetTransactions(
      self.profile.key.id(), category_id=category_id, account_id=account_id)

    return {
      'transactions': [converters.ConvertTransaction(t) for t in transactions]
    }


# Not tested


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

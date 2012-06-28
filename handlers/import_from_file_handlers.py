from exceptions import UnicodeDecodeError
from common import CommonHandler
from datastore import lookup
from datastore import models
from datastore import update
from util import ndb_json, parse_csv


# TODO: optimize, now it is too slow
class DoResolveParsedTransaction(CommonHandler):
  def HandlePost(self):
    imported_file_id = int(self.request.get('imported_file_id'))
    transaction_index = int(self.request.get('transaction_index'))
    category_ids = [int(raw_cat_id) if raw_cat_id else None
      for raw_cat_id in self.request.get('categories').split(',')]
    amounts = [float(raw_amount) if raw_amount else None
      for raw_amount in self.request.get('amounts').split(',')]
    drop = self.request.get('drop') == '1'

    imported_file = lookup.GetImportedFileById(self.profile, imported_file_id)
    parsed_transaction = imported_file.parsed_transactions[transaction_index]

    # Dropping old transactions
    if parsed_transaction.resolutions:
      transaction_ids = [t.transaction_id
                         for t in parsed_transaction.resolutions]
      update.DeleteTransactions(self.profile, transaction_ids)
      parsed_transaction.resolutions = []

    def _AddTransaction(cat_id, amount):
      transaction = update.AddTransaction(
          self.profile, amount, parsed_transaction.date,
          account_id=imported_file.account_id,
          category_id=cat_id,
          description=parsed_transaction.description,
          source='import')
      parsed_transaction.resolutions.append(
          models.ImportedFileTransaction.ResolvedTransaction(
              transaction_id=transaction.key.id(),
              amount=amount,
              category_id=cat_id))

    if not drop:
      if len(category_ids) == 1:
        _AddTransaction(category_ids[0], parsed_transaction.amount)
      else:
        for cat_id, amount in zip(category_ids, amounts):
          _AddTransaction(cat_id, amount)
    else:
      parsed_transaction.dropped = True

    imported_file.put()

    self.response.set_status(200)


class DoApplyParseSchemaToImportedFile(CommonHandler):
  def HandlePost(self):
    imported_file_id = int(self.request.get('id'))
    schema = self.request.get('schema')

    imported_file = lookup.GetImportedFileById(self.profile, imported_file_id)
    imported_file.schema = schema
    imported_file.parsed = True
    imported_file.parsed_transactions = parse_csv.ParseCsv(
        imported_file.schema, imported_file.source_file)

    _FindResolvedTransactions(self.profile, imported_file)

    # For future performance
    imported_file.source_file = None
    imported_file.put()

    self.redirect('/edit_imported_file?id=%d' % imported_file.key.id())


def _FindResolvedTransactions(profile, imported_file):
  # TODO: autodetect dropped transactions.
  # Looking for existing transactions from previous imports
  for parsed_transaction in imported_file.parsed_transactions:
    transactions = lookup.GetTransactionsForDay(
        profile, parsed_transaction.date,
        account_id=imported_file.account_id)
    import_transactions = [t for t in transactions if t.source == 'import']
    resolved_transactions = _FindMatchingTransactions(
        parsed_transaction.amount, import_transactions)
    for resolved_transaction in resolved_transactions:
      parsed_transaction.resolutions.append(
          models.ImportedFileTransaction.ResolvedTransaction(
              transaction_id=resolved_transaction.key.id(),
              amount=resolved_transaction.amount,
              category_id=resolved_transaction.category_id))


def _FindMatchingTransactions(amount, transactions):
  amounts = [t.amount for t in transactions]
  for i1, t1 in enumerate([0] + amounts):
    for i2, t2 in enumerate([0] + amounts):
      for i3, t3 in enumerate([0] + amounts):
        if abs(sum([t1, t2, t3]) - amount) < 0.001:
          results = []
          if i1 > 0: results.append(transactions[i1 - 1])
          if i2 > 0: results.append(transactions[i2 - 1])
          if i3 > 0: results.append(transactions[i3 - 1])
          return results

  return []


class DoAddTransactionsFromCsv(CommonHandler):
  def HandlePost(self):
    account_id = int(self.request.get('account_id'))
    raw_csv = self.request.get('csv')

    imported_file = models.ImportedFile(
        parent=self.profile.key,
        account_id=account_id)
    try:
      raw_csv.decode('utf-8')
    except UnicodeDecodeError:
      raw_csv = raw_csv.decode('cp1252')

    imported_file.source_file = raw_csv

    schemas = [s.schema for s in self.profile.parse_schemas]
    schema, parsed_transactions = parse_csv.AutoDetectSchema(schemas, raw_csv)

    if schema:
      imported_file.parsed = True
      imported_file.schema = schema
      imported_file.parsed_transactions = parsed_transactions
      imported_file.source_file = None
      _FindResolvedTransactions(self.profile, imported_file)

    imported_file.put()

    imported_file_list = lookup.GetOrCreateImportedFileList(self.profile)
    imported_file_list.imported_files.append(models.ImportedFileDescription(
        imported_file_id=imported_file.key.id(),
        date=imported_file.date))
    imported_file_list.put()

    self.redirect('/a/index.html#edit_imported_file/id=%d' % imported_file.key.id())


class DoAddParseSchema(CommonHandler):
  def HandlePost(self):
    name = self.request.get('name')
    schema = self.request.get('schema')

    self.profile.parse_schemas.append(
        models.ParseSchema(name=name, schema=schema))
    self.profile.put()

    # TODO: redirect to a correct url
    self.redirect('/')


# Pages


class EditImportedFilePage(CommonHandler):
  def HandleGet(self):
    imported_file_id = int(self.request.get('id'))
    imported_file = lookup.GetImportedFileById(self.profile, imported_file_id)

    template_values = {
      'imported_file': imported_file,
      'imported_transactions_json': [
          ndb_json.encode(t) for t in imported_file.parsed_transactions],
      'account': lookup.GetAccountById(self.profile, imported_file.account_id)
    }
    if imported_file.source_file:
      source_file_lines = imported_file.source_file.splitlines()
      if imported_file.schema:
        source_file_lines = [imported_file.schema] + source_file_lines
      template_values['formatted_parsed_lines'] = parse_csv.ParseCsvToPreview(
          source_file_lines)[:13]

    self.WriteToTemplate('templates/import_from_file/edit_imported_file.html',
                         template_values)


class ImportFromFilePage(CommonHandler):
  def HandleGet(self):

    template_values = {
      'imported_file_descriptions':
          lookup.GetOrCreateImportedFileList(self.profile).imported_files
    }

    self.WriteToTemplate('templates/import_from_file/import_from_file.html',
                         template_values)

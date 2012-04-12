from datetime import datetime

from google.appengine.ext import ndb
from common_handlers import CommonHandler
from datastore import models, lookup, update
import parse
import parse_csv


class DoAddAccount(CommonHandler):
  def HandlePost(self):
    name = self.request.get('name')
    currency = self.request.get('currency')
    update.AddAccount(self.profile, name, currency)

    self.redirect('/')


class DoEditTransaction(CommonHandler):
  def _UpdateBudget(self, budget_date, transaction):
    budget_key = ndb.Key(models.Budget, models.Budget.DateToStr(budget_date))
    budget = models.Budget.get_or_insert(
      budget_key.id(), parent=self.profile.key, date=budget_date)
    budget_items = [i for i in budget.items
                    if i.transaction_id == transaction.key.id()]
    if len(budget_items) == 1:
      budget_item = budget_items[0]
    else:
      budget_item = models.BudgetItem(
        date=transaction.date, transaction_id=transaction.key.id())
      budget.items.append(budget_item)
    budget_item.date = transaction.date
    budget_item.description = transaction.description
    budget_item.category_id = transaction.category_id
    budget_item.planned_amount = transaction.amount
    budget.put()

  def HandlePost(self):
    amount = parse.ParseFloat(self.request.get('amount'))
    description = self.request.get('description')
    date = datetime.strptime(self.request.get('date'), '%d.%m.%Y')
    account_id = parse.ParseInt(self.request.get('account_id'))
    category_id = parse.ParseInt(self.request.get('category_id'))
    dest_category_id = parse.ParseInt(self.request.get('dest_category_id'))
    dest_account_id = parse.ParseInt(self.request.get('dest_account_id'))
    transaction_id = parse.ParseInt(self.request.get('transaction_id'))

    raw_budget_date = self.request.get('budget_date')
    budget_date = None
    if raw_budget_date:
      budget_date = models.Budget.ParseDate(raw_budget_date)
      date = budget_date.replace(day=date.day)

    source = 'budget' if budget_date else 'manual'

    if transaction_id is not None:
      transaction = update.UpdateTransaction(
          self.profile, transaction_id, amount, date, account_id=account_id,
          category_id=category_id, description=description,
          dest_category_id=dest_category_id, dest_account_id=dest_account_id,
          source=source, planned=budget_date is not None)
    else:
      transaction = update.AddTransaction(
          self.profile, amount, date, account_id=account_id,
          category_id=category_id, description=description,
          dest_category_id=dest_category_id, dest_account_id=dest_account_id,
          source=source, planned=budget_date is not None)

    if budget_date:
      self._UpdateBudget(budget_date, transaction)

    self.response.set_status(200)


class DoEditProfile(CommonHandler):
  def HandlePost(self):
    main_currency = self.request.get('main_currency')
    password = self.request.get('password')

    kw = {}
    if main_currency:
      kw['main_currency'] = main_currency
    if password:
      kw['password'] = password

    update.UpdateProfile(self.profile, **kw)

    self.redirect('/user_settings')


class DoAddProfile(CommonHandler):
  def post(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    profile_name = self.request.get('name')

    self.profile = update.AddProfile(self.google_user, profile_name)
    update.UpdateUser(self.visitor, active_profile_id=self.profile.key.id())

    self.redirect('/')


class DoConnectToProfile(CommonHandler):
  def post(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    profile_code = self.request.get('profile_code')

    if profile_code:
      self.profile = lookup.GetProfileByCode(profile_code)
      if self.profile:
        update.AddUserToProfile(self.profile, self.google_user)
        update.UpdateUser(self.visitor, active_profile_id=self.profile.key.id())

    self.redirect('/')


class DoSetActiveProfile(CommonHandler):
  def post(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    profile_id = int(self.request.get('id'))

    if lookup.GetProfileById(profile_id):
      update.UpdateUser(self.visitor, active_profile_id=profile_id)
    else:
      raise Exception('Profile with id %r does not exist' % profile_id)

    self.redirect('/')


class DoAddCategory(CommonHandler):
  def HandlePost(self):
    name = self.request.get('name')

    update.AddCategory(self.profile, name)

    self.redirect('/')


class DoAddParseSchema(CommonHandler):
  def HandlePost(self):
    name = self.request.get('name')
    schema = self.request.get('schema')

    self.profile.parse_schemas.append(
        models.ParseSchema(name=name, schema=schema))
    self.profile.put()

    # TODO: redirect to a correct url
    self.redirect('/')


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

    self.redirect('/edit_imported_file?id=%d' % imported_file.key.id())


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

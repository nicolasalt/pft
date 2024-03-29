import datetime
from google.appengine.ext import ndb
from google.net.proto import ProtocolBuffer
from webob import exc
import common
import converters
from datastore import models, transactions
from util import  parse_csv, parse, util, currency_rates_util


class DoEditProfile(common.CommonHandler):
  def HandlePost(self, command):
    # TODO: check permissions
    profile_id = parse.ParseInt(self.request.get('profile_id'))
    name = self.request.get('name', None)
    main_currency = self.request.get('main_currency', None)

    # TODO: use JSON request
    kw = {}
    if name is not None:
      kw['name'] = name

    if command == 'add':
      kw['name'] = kw.get('name') or 'Untitled'
      main_currency = main_currency or 'USD'
      assert currency_rates_util.IsCurrencySupported(main_currency)
      kw['main_currency'] = main_currency
      profile = models.Profile.Create(self.visitor.key.id(), **kw)
      models.User.Update(
        self.visitor.key.id(), active_profile_id=profile.key.id())
    elif command == 'edit':
      profile = models.Profile.Update(profile_id, **kw)
    elif command == 'delete':
      assert profile_id is not None
      if profile_id == self.visitor.active_profile_id:
        models.User.Update(self.visitor.key.id(), active_profile_id=None)
      ndb.Key(models.Profile, profile_id).delete()
      profile = None
    else:
      raise ValueError('Command %r is not supported' % command)

    response = {'status': 'ok'}
    if profile:
      response['profile'] = converters.ConvertProfile(profile)
    return response


class DoSetActiveProfile(common.CommonHandler):
  def HandlePost(self):
    profile_id = parse.ParseInt(self.request.get('id'))

    if models.Profile.get_by_id(profile_id):
      models.User.Update(self.visitor.key.id(), active_profile_id=profile_id)
      return {'status': 'ok'}
    else:
      return {'status': 'profile_does_not_exist'}


class DoConnectToProfile(common.CommonHandler):
  def HandlePost(self):
    profile_code = self.request.get('profile_code')
    if not profile_code:
      raise exc.HTTPBadRequest('Profile code is not specified')

    try:
      profile = models.Profile.GetByCode(profile_code)
    except ProtocolBuffer.ProtocolBufferDecodeError:
      raise exc.HTTPBadRequest('Profile code %r can\'t be parsed' % profile_code)
    if not profile:
      raise exc.HTTPBadRequest('Profile for code %r does not exist' % profile_code)

    # TODO: ask the owner's permission.
    profile.AddUser(self.visitor.key.id())
    # TODO: create a helper function for this
    models.User.Update(
      self.visitor.key.id(), active_profile_id=profile.key.id())

    return {'status': 'ok'}


class DoEditAccount(common.CommonHandler):
  @common.active_profile_required
  def HandlePost(self, command):
    account_id = parse.ParseInt(self.request.get('account_id'))
    name = self.request.get('name', None)
    currency = self.request.get('currency', None)
    type = self.request.get('type', None)
    balance = parse.ParseFloat(self.request.get('balance'))

    # TODO: use JSON request
    kw = {}
    if name is not None:
      kw['name'] = name

    if command == 'add':
      kw['name'] = kw.get('name') or 'Untitled'
      if type == models.Account.Types.VIRTUAL and not currency:
        currency = self.profile.main_currency
      assert currency_rates_util.IsCurrencySupported(currency)
      kw['currency'] = currency
      if not type:
        type = models.Account.Types.PHYSICAL
      assert type in models.Account.Types.ALL
      kw['type'] = type

      account = self.profile.AddAccount(**kw)
    elif command == 'edit':
      assert account_id is not None
      account = self.profile.UpdateAccount(account_id, **kw)
    elif command == 'delete':
      assert account_id is not None
      self.profile.DeleteAccount(account_id)
      account = None
    else:
      raise ValueError('Command %r is not supported' % command)

    if account and balance is not None and abs(balance - account.balance) > 0.001:
      transactions.AddTransaction(
        self.profile.key.id(), balance - account.balance, util.DatetimeUTCNow(),
        description='Manual account balance adjust',
        dest_account_id=account.id, source='manual')
      self.ReloadProfile()

    response = {'status': 'ok'}
    if account:
      response['account'] = converters.ConvertAccount(
        self.profile.GetAccountById(account.id))
    return response


class DoEditTransaction(common.CommonHandler):
  @common.active_profile_required
  def HandlePost(self, command):
    amount = parse.ParseFloat(self.request.get('amount'))
    description = self.request.get('description')
    # TODO: use consistent date formats.
    raw_date = self.request.get('date')
    date = raw_date and datetime.datetime.strptime(raw_date, '%d.%m.%Y')
    transaction_id = parse.ParseInt(self.request.get('id'))

    if command == 'add':
      source_account_id = parse.ParseInt(self.request.get('source_account_id'))
      dest_account_id = parse.ParseInt(self.request.get('dest_account_id'))
      transaction = transactions.AddTransaction(
        self.profile.key.id(), amount, date, description=description,
        source_account_id=source_account_id, dest_account_id=dest_account_id,
        source=models.Transaction.Sources.MANUAL)
    elif command == 'edit':
      assert transaction_id is not None
      transaction = transactions.UpdateTransaction(
        self.profile.key.id(), transaction_id, amount, date, description=description)
    elif command == 'delete':
      assert transaction_id is not None
      transactions.DeleteTransaction(self.profile.key.id(), transaction_id)
      transaction = None
    else:
      raise ValueError('Command %r is not supported' % command)

    response = {'status': 'ok'}
    if transaction:
      response['transaction'] = converters.ConvertTransaction(transaction)
    return response


# Not tested


class DoAddParseSchema(common.CommonHandler):
  def HandlePost(self):
    name = self.request.get('name')
    schema = self.request.get('schema')

    self.profile.parse_schemas.append(
      models.ParseSchema(name=name, schema=schema))
    self.profile.put()

    self.WriteToJson({'status': 'ok'})


class DoApplyParseSchemaToImportedFile(common.CommonHandler):
  def HandlePost(self):
    imported_file_id = int(self.request.get('id'))
    schema = self.request.get('schema')

    imported_file = lookup.GetImportedFileById(self.profile, imported_file_id)
    imported_file.schema = schema
    imported_file.parsed = True
    imported_file.parsed_transactions = parse_csv.ParseCsv(
      imported_file.schema, imported_file.source_file)

    # For future performance
    imported_file.source_file = None
    imported_file.put()

    self.WriteToJson({'status': 'ok'})

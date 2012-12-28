import common
from datastore import models, transactions
from util import  parse_csv, parse, util


class DoAddProfile(common.CommonHandler):
  def HandlePost(self):
    profile_name = self.request.get('name')

    self.profile = models.Profile.Create(self.visitor.key.id(), profile_name)
    models.User.Update(self.visitor.key.id(), active_profile_id=self.profile.key.id())

    return {
      'id': self.profile.key.id(),
      'status': 'ok'
    }


class DoSetActiveProfile(common.CommonHandler):
  def HandlePost(self):
    profile_id = parse.ParseInt(self.request.get('id'))

    if models.Profile.get_by_id(profile_id):
      models.User.Update(self.visitor.key.id(), active_profile_id=profile_id)
      return {'status': 'ok'}
    else:
      return {'status': 'profile_does_not_exist'}


class DoEditAccount(common.CommonHandler):
  @common.active_profile_required
  def HandlePost(self, command):
    account_id = parse.ParseInt(self.request.get('account_id'))
    name = self.request.get('name', None)
    currency = self.request.get('currency', None)
    balance = parse.ParseFloat(self.request.get('balance'))

    # TODO: use JSON request
    kw = {}
    if name is not None:
      kw['name'] = name
    if currency is not None:
      kw['currency'] = currency

    if command == 'add':
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
          self.profile, balance - account.balance, util.DatetimeUTCNow(),
          description='Manual account balance adjust',
          dest_account_id=account_id, source='manual')

    response = {
      'status': 'ok'
    }
    if account:
      response['account'] = account
    return response


class DoEditCategory(common.CommonHandler):
  @common.active_profile_required
  def HandlePost(self, command):
    category_id = parse.ParseInt(self.request.get('category_id'))
    name = self.request.get('name', None)
    balance = parse.ParseFloat(self.request.get('balance'))

    # TODO: use JSON request
    kw = {}
    if name is not None:
      kw['name'] = name

    if command == 'add':
      category = self.profile.AddCategory(**kw)
    elif command == 'edit':
      assert category_id is not None
      category = self.profile.UpdateCategory(category_id, **kw)
    elif command == 'delete':
      assert category_id is not None
      self.profile.DeleteCategory(category_id)
      category = None
    else:
      raise ValueError('Command %r is not supported' % command)

    if category and balance is not None and abs(balance - category.balance) > 0.001:
      transactions.AddTransaction(
          self.profile, balance - category.balance, util.DatetimeUTCNow(),
          description='Manual category balance adjust',
          dest_category_id=category_id, source='manual')

    response = {
      'status': 'ok'
    }
    if category:
      response['category'] = category
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

from datetime import datetime
from google.appengine.ext import ndb


# TODO: is this needed?
class UserProfileSettings(ndb.Model):
  profile_id = ndb.IntegerProperty(required=True)
  cash_account_id = ndb.IntegerProperty()
  main_account_id = ndb.IntegerProperty()
  important_account_ids = ndb.IntegerProperty(repeated=True)


class User(ndb.Model):
  creation_time = ndb.DateTimeProperty(auto_now_add=True)
  active_profile_id = ndb.IntegerProperty()
  profile_settings = ndb.LocalStructuredProperty(UserProfileSettings, repeated=True)

  @staticmethod
  def MakeKey(user_id):
    return ndb.Key(User, user_id)

  @classmethod
  def Get(cls, user_id):
    user = cls.MakeKey(user_id).get()
    if not user:
      user = cls(key=cls.MakeKey(user_id))
    return user

  @classmethod
  @ndb.transactional
  def Update(cls, user_id, **kw):
    user = cls.Get(user_id)
    user.populate(**kw)
    user.put()

  def GetOrCreateProfileSettings(self, profile_id):
    for settings in self.profile_settings:
      if settings.profile_id == profile_id:
        return settings

    settings = UserProfileSettings(profile_id=profile_id)
    self.profile_settings.append(settings)

    return settings


class ParseSchema(ndb.Model):
  name = ndb.StringProperty(required=True)
  schema = ndb.StringProperty(required=True)


class Account(ndb.Model):
  id = ndb.IntegerProperty(required=True)
  name = ndb.StringProperty(required=True)
  # TODO: add automatic currency converter:
  # http://www.google.com/ig/calculator?hl=en&q=1rub=?eur
  currency = ndb.StringProperty(required=True)
  balance = ndb.FloatProperty(default=0.0)
  creation_time = ndb.DateTimeProperty(auto_now_add=True)


class Category(ndb.Model):
  id = ndb.IntegerProperty(required=True)
  name = ndb.StringProperty(required=True)
  balance = ndb.FloatProperty(default=0.0)
  creation_time = ndb.DateTimeProperty(auto_now_add=True)


class Profile(ndb.Model):
  name = ndb.StringProperty(required=True)
  owner_id = ndb.StringProperty(required=True)
  user_ids = ndb.StringProperty(repeated=True)
  creation_time = ndb.DateTimeProperty(auto_now_add=True)
  main_currency = ndb.StringProperty(default='USD')
  parse_schemas = ndb.LocalStructuredProperty(ParseSchema, repeated=True)
  # TODO: Accounts are very similar to categories: unite somehow?
  accounts = ndb.LocalStructuredProperty(Account, repeated=True)
  categories = ndb.LocalStructuredProperty(Category, repeated=True)

  @classmethod
  def GetActive(cls, user_id):
    profile_id = User.Get(user_id).active_profile_id
    if profile_id:
      return cls.get_by_id(profile_id)
    else:
      return None

  @classmethod
  def Create(cls, owner_id, name, **kw):
    profile = cls(owner_id=owner_id, name=name)
    profile.populate(**kw)
    profile.user_ids.append(owner_id)
    profile.put()
    return profile

  def AddAccount(self, **kw):
    if self.accounts:
      id = self.accounts[-1].id + 1
    else:
      id = 0
    account = Account(id=id, **kw)
    self.accounts.append(account)
    self.put()
    return account

  def UpdateAccount(self, account_id, **kw):
    account = self.GetAccountById(account_id)
    account.populate(**kw)
    self.put()
    return account

  def GetAccountById(self, account_id):
    account_dict = dict([(a.id, a) for a in self.accounts])
    assert account_id in account_dict
    return account_dict.get(account_id)

  def DeleteAccount(self, account_id):
    self.accounts = filter(lambda a: a.id != account_id, self.accounts)
    self.put()

  def AddCategory(self, **kw):
    if self.categories:
      id = self.categories[-1].id + 1
    else:
      id = 0
    category = Category(id=id, **kw)
    self.categories.append(category)
    self.put()
    return category

  def GetCategoryById(self, category_id):
    category_dict = dict([(a.id, a) for a in self.categories])
    assert category_id in category_dict
    return category_dict.get(category_id)

  def UpdateCategory(self, category_id, **kw):
    category = self.GetCategoryById(category_id)
    category.populate(**kw)
    self.put()
    return category

  def DeleteCategory(self, category_id):
    self.categories = filter(lambda c: c.id != category_id, self.categories)
    self.put()


class Transaction(ndb.Model):
  source_account_id = ndb.IntegerProperty()
  source_category_id = ndb.IntegerProperty()
  amount = ndb.FloatProperty(required=True)
  date = ndb.DateTimeProperty(required=True)
  description = ndb.StringProperty(indexed=False)
  dest_account_id = ndb.IntegerProperty()
  dest_category_id = ndb.IntegerProperty()
  source = ndb.StringProperty(
    choices=['unknown', 'import', 'manual', 'budget'],
    default='unknown')

  @classmethod
  def Get(cls, profile, transaction_id):
    return cls.get_by_id(transaction_id, parent=profile.key)


class BudgetItem(ndb.Model):
  date = ndb.DateTimeProperty()
  description = ndb.StringProperty()
  category_id = ndb.IntegerProperty()
  planned_amount = ndb.FloatProperty()
  transaction_id = ndb.IntegerProperty()


class Budget(ndb.Model):
  date = ndb.DateTimeProperty(required=True)
  items = ndb.LocalStructuredProperty(BudgetItem, repeated=True)

  DATE_FORMAT = '%m.%Y'

  def GetDateRange(self):
    start = datetime(self.date.year, self.date.month, 1)
    return start, self.GetNextBudgetDate()

  def GetNextBudgetDate(self):
    if self.date.month == 12:
      return datetime(self.date.year + 1, 1, 1)
    else:
      return datetime(self.date.year, self.date.month + 1, 1)

  def GetPreviousBudgetDate(self):
    if self.date.month == 1:
      return datetime(self.date.year - 1, 12, 1)
    else:
      return datetime(self.date.year, self.date.month - 1, 1)

  @staticmethod
  def DateToStr(date):
    return date.strftime(Budget.DATE_FORMAT)

  def GetStrDate(self):
    return Budget.DateToStr(self.date)

  @staticmethod
  def ParseDate(str_date):
    return datetime.strptime(str_date, Budget.DATE_FORMAT)


class ImportedFileTransaction(ndb.Model):
  class ResolvedTransaction(ndb.Model):
    transaction_id = ndb.IntegerProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    category_id = ndb.IntegerProperty()
    description = ndb.StringProperty()

  date = ndb.DateTimeProperty(required=True)
  amount = ndb.FloatProperty(required=True)
  description = ndb.StringProperty()
  resolutions = ndb.LocalStructuredProperty(ResolvedTransaction, repeated=True)
  dropped = ndb.BooleanProperty(default=False)


class ImportedFile(ndb.Model):
  account_id = ndb.IntegerProperty(required=True)
  date = ndb.DateTimeProperty(required=True, auto_now_add=True)
  schema = ndb.StringProperty()
  source_file = ndb.TextProperty()
  parsed = ndb.BooleanProperty(default=False)
  parsed_transactions = ndb.LocalStructuredProperty(
    ImportedFileTransaction, repeated=True)


class ImportedFileDescription(ndb.Model):
  imported_file_id = ndb.IntegerProperty(required=True)
  date = ndb.DateTimeProperty(required=True)


# Single per user
class ImportedFileList(ndb.Model):
  imported_files = ndb.LocalStructuredProperty(
    ImportedFileDescription, repeated=True)


# Single in the system
class CurrencyRates(ndb.Model):
  class Rate(ndb.Model):
    # Lowercase
    currency = ndb.StringProperty(required=True)
    # How many USD is 1 currency item.
    rate = ndb.FloatProperty(required=True)

  SUPPORTED_CURRENCIES = ['usd', 'euro', 'chf', 'rub']

  last_updated = ndb.DateTimeProperty()
  rates = ndb.LocalStructuredProperty(Rate, repeated=True)

  @classmethod
  def Get(cls):
    return cls.get_or_insert('global_currency_rates')

  @classmethod
  def Update(cls, new_rates):
    """
      Args:
        new rates: dict like {'euro': 1.34, 'rub': 0.33}
    """
    ratesModel = cls.Get()
    rates = dict([(r.currency, r.rate) for r in ratesModel.rates])
    rates.update(new_rates)
    ratesModel.rates = [cls.Rate(currency=c, rate=r)
                        for c, r in rates.iteritems()]
    ratesModel.last_updated = datetime.now()
    ratesModel.put()

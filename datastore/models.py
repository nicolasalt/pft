from datetime import datetime, timedelta
from google.appengine.ext import ndb


class User(ndb.Model):
  google_user = ndb.UserProperty(required=True)
  date = ndb.DateTimeProperty(required=True, auto_now_add=True)
  active_profile_id = ndb.IntegerProperty()

  @staticmethod
  def MakeKey(user_id):
    return ndb.Key(User, user_id)


class ParseSchema(ndb.Model):
  name = ndb.StringProperty(required=True)
  schema = ndb.StringProperty(required=True)


class Account(ndb.Model):
  name = ndb.StringProperty(required=True)
  currency = ndb.StringProperty(required=True)
  balance = ndb.FloatProperty(default=0.0)
  date = ndb.DateTimeProperty(required=True, auto_now_add=True)


class Category(ndb.Model):
  name = ndb.StringProperty(required=True)
  balance = ndb.FloatProperty(default=0.0)
  date = ndb.DateTimeProperty(required=True, auto_now_add=True)


# TODO: add accounts and categories to the profile model as structured
# properties.
class Profile(ndb.Model):
  name = ndb.StringProperty(required=True)
  owner = ndb.UserProperty(required=True)
  users = ndb.UserProperty(repeated=True)
  date = ndb.DateTimeProperty(required=True, auto_now_add=True)
  main_currency = ndb.StringProperty(default='$')
  parse_schemas = ndb.LocalStructuredProperty(ParseSchema, repeated=True)
  accounts = ndb.LocalStructuredProperty(Account, repeated=True)
  categories = ndb.LocalStructuredProperty(Category, repeated=True)


class Transaction(ndb.Model):
  account_id = ndb.IntegerProperty(required=True)
  category_id = ndb.IntegerProperty()
  amount = ndb.FloatProperty(required=True)
  date = ndb.DateTimeProperty(required=True)
  description = ndb.StringProperty()
  dest_account_id = ndb.IntegerProperty()
  dest_category_id = ndb.IntegerProperty()
  source = ndb.StringProperty(choices=['unknown', 'import', 'manual'],
                              default='unknown')


class ExpenseItem(ndb.Model):
  category_id = ndb.IntegerProperty(required=True)
  planned_value = ndb.FloatProperty()
  transaction_id = ndb.IntegerProperty()


class IncomeItem(ndb.Model):
  name = ndb.StringProperty(required=True)
  planned_value = ndb.FloatProperty()
  transaction_id = ndb.IntegerProperty()


class Budget(ndb.Model):
  date = ndb.DateTimeProperty(required=True)
  expenses = ndb.LocalStructuredProperty(ExpenseItem, repeated=True)
  income = ndb.LocalStructuredProperty(IncomeItem, repeated=True)

  DATE_FORMAT = '%m.%Y'

  def GetDateRange(self):
    month = self.date.month
    year = self.date.year
    start = datetime(year, month, 1)
    if month == 12:
      end = datetime(year + 1, 1, 1)
    else:
      end = datetime(year, month + 1, 1)
    return start, end

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

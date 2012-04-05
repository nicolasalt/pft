from google.appengine.ext import ndb


class User(ndb.Model):
  google_user = ndb.UserProperty(required=True)
  date = ndb.DateTimeProperty(required=True, auto_now_add=True)
  active_profile_id = ndb.IntegerProperty()

  @staticmethod
  def MakeKey(user_id):
    return ndb.Key(User, user_id)


class Profile(ndb.Model):
  name = ndb.UserProperty(required=True)
  owner = ndb.UserProperty(required=True)
  users = ndb.UserProperty(repeated=True)
  date = ndb.DateTimeProperty(required=True, auto_now_add=True)
  main_currency = ndb.StringProperty(default='$')
  password = ndb.StringProperty()


class Account(ndb.Model):
  owner = ndb.UserProperty(required=True)
  name = ndb.StringProperty(required=True)
  currency = ndb.StringProperty(required=True)
  balance = ndb.FloatProperty(default=0.0)
  date = ndb.DateTimeProperty(required=True, auto_now_add=True)


class Transaction(ndb.Model):
  account_id = ndb.IntegerProperty(required=True)
  amount = ndb.FloatProperty(required=True)
  date = ndb.DateTimeProperty(required=True)
  category_id = ndb.IntegerProperty()


class Category(ndb.Model):
  name = ndb.StringProperty(required=True)
  balance = ndb.FloatProperty(default=0.0)


class ExpenseItem(ndb.Model):
  category_id = ndb.IntegerProperty(required=True)
  planned_value = ndb.FloatProperty()


class IncomeItem(ndb.Model):
  name = ndb.StringProperty(required=True)
  planned_value = ndb.FloatProperty(default=0.0)


class Budget(ndb.Model):
  date = ndb.DateTimeProperty(required=True)
  expenses = ndb.StructuredProperty(ExpenseItem, repeated=True)
  income = ndb.StructuredProperty(IncomeItem, repeated=True)

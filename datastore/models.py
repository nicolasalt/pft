from google.appengine.ext import ndb


class UserSettings(ndb.Model):
  user = ndb.UserProperty(required=True)
  date = ndb.DateTimeProperty(required=True, auto_now_add=True)
  main_currency = ndb.StringProperty(default='$')

  @staticmethod
  def MakeKey(user_id):
    return ndb.Key(UserSettings, user_id)


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


class CategoryBudget(ndb.Model):
  category = ndb.StringProperty(required=True)
  planned_expense = ndb.FloatProperty()


class Budget(ndb.Model):
  date = ndb.DateTimeProperty(required=True)
  categories = ndb.StructuredProperty(CategoryBudget, repeated=True)

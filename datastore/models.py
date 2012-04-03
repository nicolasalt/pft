from google.appengine.ext import db


class UserSettings(db.Model):
  user = db.UserProperty(required=True)
  date = db.DateTimeProperty(required=True, auto_now_add=True)

  @staticmethod
  def MakeKey(user_id):
    return db.Key.from_path('User', user_id)

class Account(db.Model):
  owner = db.UserProperty(required=True)
  name = db.StringProperty(required=True)
  currency = db.StringProperty(required=True)
  balance = db.FloatProperty(required=True, default=0.0)
  date = db.DateTimeProperty(required=True, auto_now_add=True)

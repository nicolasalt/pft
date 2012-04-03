from datastore import models

def GetOrCreateUserSettings(user):
  key = models.UserSettings.MakeKey(user.user_id())
  return models.UserSettings.get_or_insert(key.id(), user=user)

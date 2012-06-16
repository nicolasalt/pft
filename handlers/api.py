from google.appengine.api import users
from common import CommonHandler
from datastore import lookup
from util import ndb_json

class GetProfile(CommonHandler):
  def HandleGet(self):
    response = {
      'google_user': self.google_user,
      'visitor': self.visitor,
      'logout_url': users.create_logout_url(self.request.uri),
      'profile': self.profile
    }
    if self.profile:
      response.update({
        'user_profile_settings': lookup.GetOrCreateUserProfileSettings(
            self.profile, self.visitor),
        'total_balance': self.GetTotalAccountBalance(),
        'categories_total_balance':
            sum([c.balance for c in self.profile.categories]),
      })

    self.WriteToJson(response)

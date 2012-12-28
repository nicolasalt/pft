import json
from google.appengine.api import users
import webapp2
from datastore import  models


class CommonHandler(webapp2.RequestHandler):
  def WriteToJson(self, template_values):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(template_values))

  def ReloadProfile(self):
    self.profile = models.Profile.GetActive(self.visitor.key.id())

  def HandleGet(self, *unused_args):
    pass

  def get(self, *args):
    self.visitor = models.User.Get(users.get_current_user().user_id())
    self.profile = None
    self.WriteToJson(self.HandleGet(*args))

  def HandlePost(self, *unused_args):
    pass

  def post(self, *args):
    self.visitor = models.User.Get(users.get_current_user().user_id())
    self.profile = None
    self.WriteToJson(self.HandlePost(*args))

def active_profile_required(fn):
  def decorator(self, *args, **kw):
    self.ReloadProfile()
    if not self.profile:
      return {'status': 'active_profile_not_selected'}

    return fn(self, *args, **kw)
  return decorator

import json
import os
from google.appengine.api import users
import webapp2
import jinja2
from datastore import lookup, models
from util import ndb_json, currency_rates_util

def currency_filter(value):
    return '{:0,.0f}'.format(value).replace(',', ' ')

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.filters['currency'] = currency_filter

class CommonHandler(webapp2.RequestHandler):
  def WriteToTemplate(self, template_name, template_values):
    template_values.update({
      'google_user': self.google_user,
      'visitor': self.visitor,
      'logout_url': users.create_logout_url(self.request.uri),
      'profile': self.profile
    })
    if self.profile:
      template_values.update({
        'user_profile_settings': lookup.GetOrCreateUserProfileSettings(
            self.profile, self.visitor),
        'accounts_json': [ndb_json.encode(a) for a in self.profile.accounts],
        'categories_json': [ndb_json.encode(c)
                            for c in self.profile.categories],
      })

    template = jinja_environment.get_template(template_name)
    self.response.out.write(template.render(template_values))

  def WriteToJson(self, template_values):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(ndb_json.encode(template_values))

  def InitUserAndProfile(self, redirect_to_choose_profile=True):
    self.google_user = users.get_current_user()
    if not self.google_user:
      return {
        'login_url': users.create_login_url(''),
        'status': 'not_logged_in'
      }

    self.visitor = models.User.Get(self.google_user.user_id())
    self.profile = models.Profile.GetActive(self.visitor.key.id())
    if not self.profile and redirect_to_choose_profile:
      return {
        'status': 'profile_not_selected'
      }

    return None

  def GetTotalAccountBalance(self):
    total = currency_rates_util.CalculateCurrencySum(
       [(a.balance, a.currency) for a in self.profile.accounts],
       self.profile.main_currency)
    return total or 0

  def HandleGet(self):
    pass

  def get(self):
    res = self.InitUserAndProfile()
    if res:
      self.WriteToJson(res)
    else:
      self.HandleGet()

  def HandlePost(self):
    pass

  def post(self):
    res = self.InitUserAndProfile()
    if res:
      self.WriteToJson(res)
    else:
      self.HandlePost()

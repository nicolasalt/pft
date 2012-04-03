import cgi
import datetime
import urllib
import webapp2
import jinja2
import os

from google.appengine.ext import db
from google.appengine.api import users
from datastore import models, lookup

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
  def get(self):
    visitor = users.get_current_user()
    if not visitor:
      self.redirect(users.create_login_url(self.request.uri))

    user_settings = lookup.GetOrCreateUserSettings(visitor)

    query = models.Account.all().ancestor(user_settings).order('-date')
    accounts = query.fetch(100)

    template_values = {
      'accounts': accounts,
    }

    template = jinja_environment.get_template('templates/index.html')
    self.response.out.write(template.render(template_values))


class DoAddAccount(webapp2.RequestHandler):
  def post(self):
    visitor = users.get_current_user()
    if not visitor:
      self.redirect(users.create_login_url(self.request.uri))

    user_settings = lookup.GetOrCreateUserSettings(visitor)

    account = models.Account(
        parent=user_settings.key(),
        owner=users.get_current_user(),
        name=self.request.get('name'),
        currency= self.request.get('currency')).put()

    self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/do/add_account', DoAddAccount)],
    debug=True)
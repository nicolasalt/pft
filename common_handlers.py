import os
from google.appengine.api import users
import webapp2
import jinja2
from datastore import lookup

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CommonHandler(webapp2.RequestHandler):
  def write_to_template(self, template_name, template_values):
    template_values.update({
      'visitor': self.visitor,
      'profile': self.profile
    })
    template = jinja_environment.get_template(template_name)
    self.response.out.write(template.render(template_values))

  def init_user_and_profile(self, redirect_to_choose_profile=True):
    self.google_user = users.get_current_user()
    if not self.google_user:
      self.redirect(users.create_login_url(self.request.uri))
      return False

    self.visitor = lookup.GetUser(self.google_user)
    self.profile = lookup.GetActiveProfile(self.google_user)
    if not self.profile and redirect_to_choose_profile:
      self.redirect('/manage_profiles')
      return False

    return True


  def handle_get(self):
    pass

  def get(self):
    if self.init_user_and_profile():
      self.handle_get()

  def handle_post(self):
    pass

  def post(self):
    if self.init_user_and_profile():
      self.handle_post()

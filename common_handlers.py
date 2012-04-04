import os
from google.appengine.api import users
import webapp2
import jinja2
from datastore import lookup

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CommonHandler(webapp2.RequestHandler):
  def write_to_template(self, template_name, template_values):
    template = jinja_environment.get_template(template_name)
    self.response.out.write(template.render(template_values))

  def init_user_settings(self):
    self.visitor = users.get_current_user()
    if not self.visitor:
      self.redirect(users.create_login_url(self.request.uri))
      return False

    self.user_settings = lookup.GetUserSettings(self.visitor)
    if not self.user_settings:
      self.redirect('/create_user')
      return False

    return True


  def handle_get(self):
    pass

  def get(self):
    if self.init_user_settings():
      self.handle_get()

  def handle_post(self):
    pass

  def post(self):
    if self.init_user_settings():
      self.handle_post()

import os
from google.appengine.api import users
import webapp2
import jinja2
from datastore import lookup

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CommonHandler(webapp2.RequestHandler):
  def WriteToTemplate(self, template_name, template_values):
    template_values.update({
      'google_user': self.google_user,
      'visitor': self.visitor,
      'logout_url': users.create_logout_url(self.request.uri),
      'profile': self.profile
    })
    template = jinja_environment.get_template(template_name)
    self.response.out.write(template.render(template_values))

  def InitUserAndProfile(self, redirect_to_choose_profile=True):
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


  def HandleGet(self):
    pass

  def get(self):
    if self.InitUserAndProfile():
      self.HandleGet()

  def HandlePost(self):
    pass

  def post(self):
    if self.InitUserAndProfile():
      self.HandlePost()

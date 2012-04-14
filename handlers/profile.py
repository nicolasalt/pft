from exceptions import Exception
from common_handlers import CommonHandler
from datastore import update, lookup


class DoEditProfile(CommonHandler):
  def HandlePost(self):
    main_currency = self.request.get('main_currency')
    password = self.request.get('password')

    kw = {}
    if main_currency:
      kw['main_currency'] = main_currency
    if password:
      kw['password'] = password

    update.UpdateProfile(self.profile, **kw)

    self.redirect('/edit_profile')


class DoAddProfile(CommonHandler):
  def post(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    profile_name = self.request.get('name')

    self.profile = update.AddProfile(self.google_user, profile_name)
    update.UpdateUser(self.visitor, active_profile_id=self.profile.key.id())

    self.redirect('/')


class DoConnectToProfile(CommonHandler):
  def post(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    profile_code = self.request.get('profile_code')

    if profile_code:
      self.profile = lookup.GetProfileByCode(profile_code)
      if self.profile:
        update.AddUserToProfile(self.profile, self.google_user)
        update.UpdateUser(self.visitor, active_profile_id=self.profile.key.id())

    self.redirect('/')


class DoSetActiveProfile(CommonHandler):
  def post(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    profile_id = int(self.request.get('id'))

    if lookup.GetProfileById(profile_id):
      update.UpdateUser(self.visitor, active_profile_id=profile_id)
    else:
      raise Exception('Profile with id %r does not exist' % profile_id)

    self.redirect('/')


class ManageProfilesPage(CommonHandler):
  def get(self):
    if not self.InitUserAndProfile(redirect_to_choose_profile=False):
      return

    template_values = {
      'profiles': lookup.GetAllProfiles(self.google_user),
    }

    self.WriteToTemplate('templates/profile/manage_profiles.html',
                         template_values)


class EditProfile(CommonHandler):
  def HandleGet(self):
    self.WriteToTemplate('templates/profile/edit_profile.html', {})

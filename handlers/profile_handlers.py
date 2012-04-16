from datetime import datetime
from exceptions import Exception
from common import CommonHandler
from datastore import update, lookup
from util import  parse


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

    self.redirect('/settings')


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


class DoEditCategory(CommonHandler):
  def HandlePost(self):
    category_id = parse.ParseInt(self.request.get('category_id'))
    name = self.request.get('name')
    balance = parse.ParseFloat(self.request.get('balance'))
    # TODO: implement delete category
    delete = self.request.get('delete') == '1'

    if category_id is not None:
      category = update.EditCategory(self.profile, category_id, name)
    else:
      category = update.AddCategory(self.profile, name)
      # TODO: looks like we need another ids, that are properties of the
      # category model
      category_id = len(self.profile.categories) - 1

    if balance is not None and abs(balance - category.balance) > 0.001:
      update.AddTransaction(
          self.profile, balance - category.balance, datetime.now(),
          description='Manual category balance adjust',
          dest_category_id=category_id, source='manual')

    self.response.set_status(200)


class DoEditAccount(CommonHandler):
  def HandlePost(self):
    account_id = parse.ParseInt(self.request.get('account_id'))
    name = self.request.get('name')
    currency = self.request.get('currency')
    balance = parse.ParseFloat(self.request.get('balance'))
    # TODO: implement delete account
    delete = self.request.get('delete') == '1'

    if account_id is not None:
      account = update.EditAccount(self.profile, account_id, name, currency)
    else:
      account = update.AddAccount(self.profile, name, currency)
      account_id = len(self.profile.accounts) - 1

    if balance is not None and abs(balance - account.balance) > 0.001:
      update.AddTransaction(
          self.profile, balance - account.balance, datetime.now(),
          description='Manual account balance adjust',
          dest_account_id=account_id, source='manual')

    self.response.set_status(200)


class DoEditUserProfileSettings(CommonHandler):
  def HandlePost(self):
    cash_account_id = parse.ParseInt(self.request.get('cash_account_id'))
    main_account_id = parse.ParseInt(self.request.get('main_account_id'))
    important_account_ids = set()
    for arg in self.request.arguments():
      if arg[:18] == 'important_account_':
        important_account_ids.add(int(arg[18:]))

    if cash_account_id is not None:
      important_account_ids.add(cash_account_id)
    if main_account_id is not None:
      important_account_ids.add(main_account_id)

    settings = lookup.GetOrCreateUserProfileSettings(self.profile, self.visitor)

    settings.cash_account_id = cash_account_id
    settings.main_account_id = main_account_id
    settings.important_account_ids = important_account_ids

    self.visitor.put()

    self.redirect('/settings')


# Pages


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
    categories_total_balance = sum([c.balance for c in self.profile.categories])

    template_values = {
      'total_balance': self.GetTotalAccountBalance(),
      'categories_total_balance': categories_total_balance
    }

    self.WriteToTemplate('templates/profile/settings.html', template_values)

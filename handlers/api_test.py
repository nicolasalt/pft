from datastore import models
import testing


class GetProfileTestCase(testing.BaseTestCase):
  def testNoProfile(self):
    response = self.testapp.get('/api/get_active_profile')

    self.assertEqual(
      {
        'status': 'active_profile_not_selected'
      },
      response.json)


class DoSetActiveProfileTestCase(testing.BaseTestCase):
  def testNormal(self):
    response = self.testapp.post('/api/do/add_profile', {'name': 'Test profile name'})
    self.profile1_id = response.json['id']
    response = self.testapp.post('/api/do/add_profile', {'name': 'Test profile name2'})
    self.profile2_id = response.json['id']

    response = self.testapp.get('/api/get_active_profile')

    self.assertEqual(self.profile2_id, response.json['user_profile_settings']['profile_id'])
    self.assertEqual(self.profile2_id, response.json['visitor']['active_profile_id'])

    response = self.testapp.post('/api/do/set_active_profile', {'id': self.profile1_id})
    self.assertEqual('ok', response.json['status'])

    response = self.testapp.get('/api/get_active_profile')
    self.assertEqual(self.profile1_id, response.json['user_profile_settings']['profile_id'])
    self.assertEqual(self.profile1_id, response.json['visitor']['active_profile_id'])

  def testProfileDoesNotExist(self):
    response = self.testapp.post('/api/do/set_active_profile', {'id': 123})
    self.assertEqual('profile_does_not_exist', response.json['status'])


class DoEditAccountTestCase(testing.BaseTestCase):
  def setUp(self):
    super(DoEditAccountTestCase, self).setUp()

    self.testapp.post('/api/do/add_profile', {'name': 'Test profile name'})

  def _AssertAccount(self, account_dict, account_id, name, currency, balance):
    self.assertEqual(account_id, account_dict['id'])
    self.assertEqual(name, account_dict['name'])
    self.assertEqual(currency, account_dict['currency'])
    self.assertAlmostEqual(balance, account_dict['balance'])

  # TODO: add more tests
  # TODO: check transactions
  def testNormal(self):
    # Adding first account
    response = self.testapp.post(
      '/api/do/account/add',
      {
        'name': 'Test account name',
        'currency': 'RUB',
        'balance': 10.0
      })
    self.account1_id = response.json['account']['id']
    self._AssertAccount(response.json['account'],
                        self.account1_id, 'Test account name', 'RUB', 10.0)

    response = self.testapp.get('/api/get_active_profile')
    self.assertEqual(1, len(response.json['profile']['accounts']))
    self._AssertAccount(response.json['profile']['accounts'][0],
                        self.account1_id, 'Test account name', 'RUB', 10.0)

    # Adding second account
    response = self.testapp.post(
      '/api/do/account/add',
      {
        'name': 'Test account name2',
        'currency': 'CHF'
      })
    self.account2_id = response.json['account']['id']
    self._AssertAccount(response.json['account'],
                        self.account2_id, 'Test account name2', 'CHF', 0.0)

    response = self.testapp.get('/api/get_active_profile')
    self.assertEqual(2, len(response.json['profile']['accounts']))
    self._AssertAccount(response.json['profile']['accounts'][1],
                        self.account2_id, 'Test account name2', 'CHF', 0.0)

    # Changing name of the first account
    response = self.testapp.post(
      '/api/do/account/edit',
      {
        'account_id': self.account1_id,
        'name': 'Test account name modified',
        'balance': 5.0
      })
    self._AssertAccount(response.json['account'],
                        self.account1_id, 'Test account name modified', 'RUB', 5.0)

    response = self.testapp.get('/api/get_active_profile')
    self.assertEqual(2, len(response.json['profile']['accounts']))
    self._AssertAccount(response.json['profile']['accounts'][0],
                        self.account1_id, 'Test account name modified', 'RUB', 5.0)

    # Deleting first account
    response = self.testapp.post(
      '/api/do/account/delete',
      {
        'account_id': self.account1_id
      })

    response = self.testapp.get('/api/get_active_profile')
    self.assertEqual(1, len(response.json['profile']['accounts']))
    self._AssertAccount(response.json['profile']['accounts'][0],
                        self.account2_id, 'Test account name2', 'CHF', 0.0)


class DoEditCategoryTestCase(testing.BaseTestCase):
  def setUp(self):
    super(DoEditCategoryTestCase, self).setUp()

    self.testapp.post('/api/do/add_profile', {'name': 'Test profile name'})

  def _AssertCategory(self, category_dict, category_id, name, balance):
    self.assertEqual(category_id, category_dict['id'])
    self.assertEqual(name, category_dict['name'])
    self.assertAlmostEqual(balance, category_dict['balance'])

  # TODO: add more tests
  # TODO: check transactions
  def testNormal(self):
    # Adding first category
    response = self.testapp.post(
      '/api/do/category/add',
      {
        'name': 'Test category name',
        'balance': 10.0
      })
    self.category1_id = response.json['category']['id']
    self._AssertCategory(response.json['category'],
                         self.category1_id, 'Test category name', 10.0)

    response = self.testapp.get('/api/get_active_profile')
    self.assertEqual(1, len(response.json['profile']['categories']))
    self._AssertCategory(response.json['profile']['categories'][0],
                         self.category1_id, 'Test category name', 10.0)

    # Adding second category
    response = self.testapp.post(
      '/api/do/category/add',
      {
        'name': 'Test category name2'
      })
    self.category2_id = response.json['category']['id']
    self._AssertCategory(response.json['category'],
                         self.category2_id, 'Test category name2', 0.0)

    response = self.testapp.get('/api/get_active_profile')
    self.assertEqual(2, len(response.json['profile']['categories']))
    self._AssertCategory(response.json['profile']['categories'][1],
                         self.category2_id, 'Test category name2', 0.0)

    # Modifying first category
    response = self.testapp.post(
      '/api/do/category/edit',
      {
        'category_id': self.category1_id,
        'name': 'Test category name modified',
        'balance': 20.0
      })
    self._AssertCategory(response.json['category'],
                         self.category1_id, 'Test category name modified', 20.0)

    response = self.testapp.get('/api/get_active_profile')
    self.assertEqual(2, len(response.json['profile']['categories']))
    self._AssertCategory(response.json['profile']['categories'][0],
                         self.category1_id, 'Test category name modified', 20.0)

    # Deleting first category
    response = self.testapp.post(
      '/api/do/category/delete',
      {
        'category_id': self.category1_id
      })

    response = self.testapp.get('/api/get_active_profile')
    self.assertEqual(1, len(response.json['profile']['categories']))
    self._AssertCategory(response.json['profile']['categories'][0],
                         self.category2_id, 'Test category name2', 0.0)


class ScenarioProfileTestCase(testing.BaseTestCase):
  def testNormal(self):
    response = self.testapp.post('/api/do/add_profile', {'name': 'Test profile name'})
    self.assertEqual('ok', response.json['status'])

    # TODO: don't use raw db access, use API instead.

    profile = models.Profile.GetActive(self.visitor_id)
    profile.AddAccount(name='Test account1', currency='USD', balance=10.0)
    profile.AddAccount(name='Test account2', currency='CHF', balance=20.0)
    profile.AddCategory(name='Test category1', balance=5.0)
    profile.AddCategory(name='Test category2', balance=6.0)

    response = self.testapp.get('/api/get_active_profile')

    self.assertEqual(
      {'profile': {
        'accounts': [
          {'balance': 10.0,
           'creation_time': '2010-12-27T00:00:00',
           'currency': 'USD',
           'id': 0,
           'name': 'Test account1'},
          {'balance': 20.0,
           'creation_time': '2010-12-27T00:00:00',
           'currency': 'CHF',
           'id': 1,
           'name': 'Test account2'}],
        'categories': [
          {'balance': 5.0,
           'creation_time': '2010-12-27T00:00:00',
           'id': 0,
           'name': 'Test category1'},
          {'balance': 6.0,
           'creation_time': '2010-12-27T00:00:00',
           'id': 1,
           'name': 'Test category2'}],
        'creation_time': '2010-12-27T00:00:00',
        'id': 1,
        'main_currency': 'USD',
        'name': 'Test profile name',
        'owner_id': '10001',
        'parse_schemas': [],
        'user_ids': ['10001']},
       'total_balance': 40.0,
       'user_profile_settings': {
         'cash_account_id': None,
         'important_account_ids': [],
         'main_account_id': None,
         'profile_id': 1},
       'visitor': {
         'active_profile_id': 1,
         'creation_time': '2010-12-27T00:00:00',
         'id': '10001',
         'profile_settings': [
           {'cash_account_id': None,
            'important_account_ids': [],
            'main_account_id': None,
            'profile_id': 1}]}},
      response.json)

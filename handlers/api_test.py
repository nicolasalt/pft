import testing


class GetProfileTestCase(testing.BaseTestCase):
  def testNoProfile(self):
    response = self.testapp.get('/api/profile/active')

    self.assertEqual(
      {'status': 'active_profile_not_selected'},
      response.json)


class GetProfilesTestCase(testing.BaseTestCase):
  def testNoProfiles(self):
    response = self.testapp.get('/api/profile/all')
    self.assertEqual(0, len(response.json['profiles']))

  def testNormal(self):
    response = self.testapp.post('/api/do/profile/add', {'name': 'Test profile name'})
    self.profile1_id = response.json['profile']['id']
    response = self.testapp.post('/api/do/profile/add', {'name': 'Test profile name2'})
    self.profile2_id = response.json['profile']['id']

    self.LogIn(self.google_user2)
    self.testapp.post('/api/do/profile/add', {'name': 'Test profile name3'})
    self.LogIn(self.google_user)

    response = self.testapp.get('/api/profile/all')
    profiles = response.json['profiles']
    self.assertEqual(2, len(profiles))
    self.assertEqual(self.profile1_id, profiles[0]['id'])
    self.assertEqual('Test profile name', profiles[0]['name'])
    self.assertEqual(self.profile2_id, profiles[1]['id'])
    self.assertEqual('Test profile name2', profiles[1]['name'])


class DoSetActiveProfileTestCase(testing.BaseTestCase):
  def testNormal(self):
    response = self.testapp.post('/api/do/profile/add', {'name': 'Test profile name'})
    self.profile1_id = response.json['profile']['id']
    response = self.testapp.post('/api/do/profile/add', {'name': 'Test profile name2'})
    self.profile2_id = response.json['profile']['id']

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(self.profile2_id, response.json['active_profile']['id'])

    response = self.testapp.post('/api/do/set_active_profile', {'id': self.profile1_id})
    self.assertEqual('ok', response.json['status'])

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(self.profile1_id, response.json['active_profile']['id'])

  def testProfileDoesNotExist(self):
    response = self.testapp.post('/api/do/set_active_profile', {'id': 123})
    self.assertEqual('profile_does_not_exist', response.json['status'])


class DoAddEditDeleteProfileTestCase(testing.BaseTestCase):
  def _AssertProfile(self, profile_dict, profile_id, name, main_currency):
    self.assertEqual(profile_id, profile_dict['id'])
    self.assertEqual(name, profile_dict['name'])
    self.assertEqual(main_currency, profile_dict['main_currency'])

  def testAdd(self):
    response = self.testapp.post('/api/do/profile/add', {
      'name': 'Test profile name',
      'main_currency': 'CHF'})
    self.profile1_id = response.json['profile']['id']
    self._AssertProfile(response.json['profile'], self.profile1_id, 'Test profile name', 'CHF')
    response = self.testapp.get('/api/profile/active')
    self._AssertProfile(response.json['active_profile'], self.profile1_id, 'Test profile name',
                        'CHF')

  def testAddEmptyProfile(self):
    response = self.testapp.post('/api/do/profile/add', {})
    self.profile1_id = response.json['profile']['id']
    self._AssertProfile(response.json['profile'], self.profile1_id, 'Untitled', 'USD')

  def testEdit(self):
    response = self.testapp.post('/api/do/profile/add', {
      'name': 'Test profile name',
      'main_currency': 'CHF'})
    self.profile1_id = response.json['profile']['id']

    response = self.testapp.post('/api/do/profile/edit', {
      'profile_id': self.profile1_id,
      'main_currency': 'RUB'})
    self._AssertProfile(response.json['profile'], self.profile1_id, 'Test profile name', 'RUB')
    response = self.testapp.get('/api/profile/active')
    self._AssertProfile(response.json['active_profile'], self.profile1_id,
                        'Test profile name', 'RUB')

  def testDelete(self):
    response = self.testapp.post('/api/do/profile/add', {'name': 'Test profile name'})
    self.profile1_id = response.json['profile']['id']
    response = self.testapp.post('/api/do/profile/add', {'name': 'Test profile name2'})
    self.profile2_id = response.json['profile']['id']

    response = self.testapp.post('/api/do/profile/delete', {'profile_id': self.profile2_id})

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(
      {'status': 'active_profile_not_selected'},
      response.json)


class DoConnectToProfileTestCase(testing.BaseTestCase):
  def setUp(self):
    super(DoConnectToProfileTestCase, self).setUp()

    response = self.testapp.post('/api/do/profile/add', {'name': 'Test profile name'})
    self.profile1_id = response.json['profile']['id']
    self.profile1_code = response.json['profile']['profile_code']

    self.LogIn(self.google_user2)

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(
      {'status': 'active_profile_not_selected'},
      response.json)

  def testNormal(self):
    response = self.testapp.post('/api/do/profile/connect', {'profile_code': self.profile1_code})
    self.assertEqual('ok', response.json['status'])

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(self.profile1_id, response.json['active_profile']['id'])

  def testProfileCodeIsNotSpecified(self):
    self.testapp.post('/api/do/profile/connect', status=400)

  def testProfileCodeCannotBeParsed(self):
    self.testapp.post('/api/do/profile/connect', {'profile_code': 'fake code'}, status=400)

  def testProfileWithTheGivenCodeDoesNotExist(self):
    self.LogIn(self.google_user)
    self.testapp.post('/api/do/profile/delete', {'profile_id': self.profile1_id})
    self.LogIn(self.google_user2)

    self.testapp.post('/api/do/profile/connect', {'profile_code': 'fake code'}, status=400)


class DoEditAccountTestCase(testing.BaseTestCase):
  def setUp(self):
    super(DoEditAccountTestCase, self).setUp()

    self.testapp.post('/api/do/profile/add', {'name': 'Test profile name'})

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

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(1, len(response.json['active_profile']['accounts']))
    self._AssertAccount(response.json['active_profile']['accounts'][0],
                        self.account1_id, 'Test account name', 'RUB', 10.0)
    self.assertEqual(0.3, response.json['total_balance'])

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

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(2, len(response.json['active_profile']['accounts']))
    self._AssertAccount(response.json['active_profile']['accounts'][1],
                        self.account2_id, 'Test account name2', 'CHF', 0.0)
    self.assertEqual(0.3, response.json['total_balance'])

    # Check transactions
    response = self.testapp.get('/api/transaction/query')
    transactions = response.json['transactions']
    self.assertEqual(1, len(transactions))
    self.assertEqual(self.account1_id, transactions[0]['dest_account_id'])
    self.assertAlmostEqual(10.0, transactions[0]['amount'])

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

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(2, len(response.json['active_profile']['accounts']))
    self._AssertAccount(response.json['active_profile']['accounts'][0],
                        self.account1_id, 'Test account name modified', 'RUB', 5.0)
    self.assertEqual(0.15, response.json['total_balance'])

    # Deleting first account
    response = self.testapp.post(
      '/api/do/account/delete',
      {
        'account_id': self.account1_id
      })

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(1, len(response.json['active_profile']['accounts']))
    self._AssertAccount(response.json['active_profile']['accounts'][0],
                        self.account2_id, 'Test account name2', 'CHF', 0.0)
    self.assertEqual(0.0, response.json['total_balance'])


class DoEditCategoryTestCase(testing.BaseTestCase):
  def setUp(self):
    super(DoEditCategoryTestCase, self).setUp()

    self.testapp.post('/api/do/profile/add', {'name': 'Test profile name'})

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

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(1, len(response.json['active_profile']['categories']))
    self._AssertCategory(response.json['active_profile']['categories'][0],
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

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(2, len(response.json['active_profile']['categories']))
    self._AssertCategory(response.json['active_profile']['categories'][1],
                         self.category2_id, 'Test category name2', 0.0)

    # Check transactions
    response = self.testapp.get('/api/transaction/query')
    transactions = response.json['transactions']
    self.assertEqual(1, len(transactions))
    self.assertEqual(self.category1_id, transactions[0]['dest_category_id'])
    self.assertAlmostEqual(10.0, transactions[0]['amount'])

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

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(2, len(response.json['active_profile']['categories']))
    self._AssertCategory(response.json['active_profile']['categories'][0],
                         self.category1_id, 'Test category name modified', 20.0)

    # Deleting first category
    response = self.testapp.post(
      '/api/do/category/delete',
      {
        'category_id': self.category1_id
      })

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(1, len(response.json['active_profile']['categories']))
    self._AssertCategory(response.json['active_profile']['categories'][0],
                         self.category2_id, 'Test category name2', 0.0)


class ScenarioProfileTestCase(testing.BaseTestCase):
  def _GenerateExpectedProfile(self):
    return {
      'active_profile': {
        'accounts': [
          {
            'balance': 10.0,
            'creation_time': '2010-12-27T00:00:00',
            'currency': 'USD',
            'id': 0,
            'name': 'Test account1'
          },
          {
            'balance': 20.0,
            'creation_time': '2010-12-27T00:00:00',
            'currency': 'CHF',
            'id': 1,
            'name': 'Test account2'
          }
        ],
        'categories': [
          {
            'balance': 5.0,
            'creation_time': '2010-12-27T00:00:00',
            'id': self.category1_id,
            'name': 'Test category1'},
          {
            'balance': 6.0,
            'creation_time': '2010-12-27T00:00:00',
            'id': self.category2_id,
            'name': 'Test category2'
          }
        ],
        'creation_time': '2010-12-27T00:00:00',
        'id': 1,
        'main_currency': 'USD',
        'name': 'Test profile name',
        'profile_code': 'agx0ZXN0YmVkLXRlc3RyDQsSB1Byb2ZpbGUYAQw'
      },
      'total_balance': 40.0,
      'user_profile_settings': {
        'cash_account_id': None,
        'important_account_ids': [],
        'main_account_id': None
      }
    }

  def testNormal(self):
    response = self.testapp.post('/api/do/profile/add', {'name': 'Test profile name'})
    self.assertEqual('ok', response.json['status'])

    # Accounts
    response = self.testapp.post(
      '/api/do/account/add',
      {'name': 'Test account1', 'currency': 'USD', 'balance': 10.0})
    self.account1_id = response.json['account']['id']
    response = self.testapp.post(
      '/api/do/account/add',
      {'name': 'Test account2', 'currency': 'CHF', 'balance': 20.0})
    self.account2_id = response.json['account']['id']

    # Categories
    response = self.testapp.post(
      '/api/do/category/add',
      {'name': 'Test category1', 'balance': 5.0})
    self.category1_id = response.json['category']['id']
    response = self.testapp.post(
      '/api/do/category/add',
      {'name': 'Test category2', 'balance': 6.0})
    self.category2_id = response.json['category']['id']

    response = self.testapp.get('/api/profile/active')
    self.assertEqual(self._GenerateExpectedProfile(), response.json)

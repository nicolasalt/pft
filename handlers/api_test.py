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

    models.CurrencyRates.Update({
      'usd': 1.0,
      'chf': 1.5
    })

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

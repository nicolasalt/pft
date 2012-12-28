from datastore import models, transactions
import testing


class AddTransactionTestCase(testing.BaseTestCase):
  def setUp(self):
    super(AddTransactionTestCase, self).setUp()

    self.AddProfile()

    profile = models.Profile.GetActive(self.visitor_id)
    self.profile_id = profile.key.id()
    self.account1_id = profile.AddAccount(name='Test account1', currency='USD').id
    self.account2_id = profile.AddAccount(name='Test account2', currency='CHF').id
    self.category1_id = profile.AddCategory(name='Test category1').id
    self.category2_id = profile.AddCategory(name='Test category2').id

  def testIncomeToAccount(self):
    transactions.AddTransaction(self.profile_id, 10.0, self.now, dest_account_id=self.account1_id)

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(10.0, profile.GetAccountById(self.account1_id).balance)

  def testTransferBetweenAccount(self):
    transactions.AddTransaction(
      self.profile_id, 10.0, self.now,
      source_account_id=self.account1_id, dest_account_id=self.account2_id)

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(-10.0, profile.GetAccountById(self.account1_id).balance)
    self.assertAlmostEqual(6.66666666, profile.GetAccountById(self.account2_id).balance)

  def testChangeCategoryBalance(self):
    transactions.AddTransaction(
      self.profile_id, 10.0, self.now, dest_category_id=self.category1_id)

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(10.0, profile.GetCategoryById(self.category1_id).balance)

  def testTransferBetweenCategories(self):
    transactions.AddTransaction(
      self.profile_id, 10.0, self.now,
      source_category_id=self.category1_id, dest_category_id=self.category2_id)

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(-10.0, profile.GetCategoryById(self.category1_id).balance)
    self.assertAlmostEqual(10.0, profile.GetCategoryById(self.category2_id).balance)

  def testOnlySourceAccountIsSpecified(self):
    self.assertRaises(
      ValueError, transactions.AddTransaction, self.profile_id, 10.0, self.now,
      source_account_id=self.account1_id)

  def testOnlySourceCategoryIsSpecified(self):
    self.assertRaises(
      ValueError, transactions.AddTransaction, self.profile_id, 10.0, self.now,
      source_category_id=self.category1_id)

  def testDestCategoryId_TogetherWithDestAccountId(self):
    self.assertRaises(
      ValueError, transactions.AddTransaction, self.profile_id, 10.0, self.now,
      dest_account_id=self.account1_id, dest_category_id=self.category1_id)

  def testNeitherAccountNorCategoryIdsAreSpecified(self):
    self.assertRaises(
      ValueError, transactions.AddTransaction, self.profile_id, 10.0, self.now)


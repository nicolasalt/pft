import datetime
from datastore import models, transactions
import testing


class AddTransactionTestCase(testing.BaseTestCase):
  def setUp(self):
    super(AddTransactionTestCase, self).setUp()

    self.AddProfile()
    self.AddAccountsAndCategories()

  def testIncomeToAccount(self):
    transaction_id = transactions.AddTransaction(
      self.profile_id, 10.0, self.now, dest_account_id=self.account1_id).key.id()

    transaction = models.Transaction.Get(self.profile_id, transaction_id)
    self.assertEqual(10.0, transaction.amount)
    self.assertEqual(self.account1_id, transaction.dest_account_id)
    self.assertEqual(self.now, transaction.date)

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(10.0, profile.GetAccountById(self.account1_id).balance)

  def testTransferBetweenAccounts(self):
    transaction_id = transactions.AddTransaction(
      self.profile_id, 10.0, self.now,
      source_account_id=self.account1_id, dest_account_id=self.account2_id).key.id()

    transaction = models.Transaction.Get(self.profile_id, transaction_id)
    self.assertEqual(10.0, transaction.amount)
    self.assertEqual(self.account1_id, transaction.source_account_id)
    self.assertEqual(self.account2_id, transaction.dest_account_id)
    self.assertEqual(self.now, transaction.date)

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(-10.0, profile.GetAccountById(self.account1_id).balance)
    self.assertAlmostEqual(6.66666666, profile.GetAccountById(self.account2_id).balance)

  def testChangeCategoryBalance(self):
    transaction_id = transactions.AddTransaction(
      self.profile_id, 10.0, self.now, dest_category_id=self.category1_id).key.id()

    transaction = models.Transaction.Get(self.profile_id, transaction_id)
    self.assertEqual(10.0, transaction.amount)
    self.assertEqual(self.category1_id, transaction.dest_category_id)
    self.assertEqual(self.now, transaction.date)

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(10.0, profile.GetCategoryById(self.category1_id).balance)

  def testTransferBetweenCategories(self):
    transaction_id = transactions.AddTransaction(
      self.profile_id, 10.0, self.now,
      source_category_id=self.category1_id, dest_category_id=self.category2_id).key.id()

    transaction = models.Transaction.Get(self.profile_id, transaction_id)
    self.assertEqual(10.0, transaction.amount)
    self.assertEqual(self.category1_id, transaction.source_category_id)
    self.assertEqual(self.category2_id, transaction.dest_category_id)
    self.assertEqual(self.now, transaction.date)

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


class UpdateTransactionTestCase(testing.BaseTestCase):
  def setUp(self):
    super(UpdateTransactionTestCase, self).setUp()

    self.AddProfile()
    self.AddAccountsAndCategories()

    self.new_date = datetime.datetime(2011, 5, 30)

  def testTransferBetweenAccounts(self):
    transaction_id = transactions.AddTransaction(
      self.profile_id, 10.0, self.now,
      source_account_id=self.account1_id, dest_account_id=self.account2_id).key.id()

    transactions.UpdateTransaction(self.profile_id, transaction_id, 5.0, self.new_date)

    transaction = models.Transaction.Get(self.profile_id, transaction_id)
    self.assertEqual(5.0, transaction.amount)
    self.assertEqual(self.account1_id, transaction.source_account_id)
    self.assertEqual(self.account2_id, transaction.dest_account_id)
    self.assertEqual(self.new_date, transaction.date)

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(-5.0, profile.GetAccountById(self.account1_id).balance)
    self.assertAlmostEqual(3.33333333, profile.GetAccountById(self.account2_id).balance)

  def testTransferBetweenCategories(self):
    transaction_id = transactions.AddTransaction(
      self.profile_id, 10.0, self.now,
      source_category_id=self.category1_id, dest_category_id=self.category2_id).key.id()

    transactions.UpdateTransaction(self.profile_id, transaction_id, 5.0, self.new_date)

    transaction = models.Transaction.Get(self.profile_id, transaction_id)
    self.assertEqual(5.0, transaction.amount)
    self.assertEqual(self.category1_id, transaction.source_category_id)
    self.assertEqual(self.category2_id, transaction.dest_category_id)
    self.assertEqual(self.new_date, transaction.date)

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(-5.0, profile.GetCategoryById(self.category1_id).balance)
    self.assertAlmostEqual(5.0, profile.GetCategoryById(self.category2_id).balance)


class DeleteTransactionsTestCase(testing.BaseTestCase):
  def setUp(self):
    super(DeleteTransactionsTestCase, self).setUp()

    self.AddProfile()
    self.AddAccountsAndCategories()

  def testNormal(self):
    transaction_id1 = transactions.AddTransaction(
      self.profile_id, 10.0, self.now, dest_account_id=self.account1_id).key.id()
    transaction_id2 = transactions.AddTransaction(
      self.profile_id, 100.0, self.now,
      source_account_id=self.account1_id, dest_account_id=self.account2_id).key.id()
    transaction_id3 = transactions.AddTransaction(
      self.profile_id, 5.0, self.now,
      dest_category_id=self.category1_id).key.id()
    transaction_id4 = transactions.AddTransaction(
      self.profile_id, 50.0, self.now,
      source_category_id=self.category1_id, dest_category_id=self.category2_id).key.id()

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(-90.0, profile.GetAccountById(self.account1_id).balance)
    self.assertAlmostEqual(66.66666666, profile.GetAccountById(self.account2_id).balance)
    self.assertAlmostEqual(-45.0, profile.GetCategoryById(self.category1_id).balance)
    self.assertAlmostEqual(50.0, profile.GetCategoryById(self.category2_id).balance)

    transactions.DeleteTransactions(
      self.profile_id, [transaction_id1, transaction_id2, transaction_id3, transaction_id4])

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(0.0, profile.GetAccountById(self.account1_id).balance)
    self.assertAlmostEqual(0.0, profile.GetAccountById(self.account2_id).balance)
    self.assertAlmostEqual(0.0, profile.GetCategoryById(self.category1_id).balance)
    self.assertAlmostEqual(0.0, profile.GetCategoryById(self.category2_id).balance)

    self.assertIsNone(models.Transaction.Get(self.profile_id, transaction_id1))
    self.assertIsNone(models.Transaction.Get(self.profile_id, transaction_id2))
    self.assertIsNone(models.Transaction.Get(self.profile_id, transaction_id3))
    self.assertIsNone(models.Transaction.Get(self.profile_id, transaction_id4))

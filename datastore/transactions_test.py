import datetime
from datastore import models, transactions
import testing


class BaseTransactionTestCase(testing.BaseTestCase):
  def setUp(self):
    super(BaseTransactionTestCase, self).setUp()

    # Adding profile
    self.profile = models.Profile.Create(self.visitor_id, name='Test profile')
    models.User.Update(self.visitor_id, active_profile_id=self.profile.key.id())

    # Adding accounts
    profile = models.Profile.GetActive(self.visitor_id)
    self.profile_id = profile.key.id()
    self.account1_id = profile.AddAccount(
      name='Test account1', currency='USD', type=models.Account.Types.PHYSICAL).id
    self.account2_id = profile.AddAccount(
      name='Test account2', currency='CHF', type=models.Account.Types.PHYSICAL).id
    self.v_account1_id = profile.AddAccount(
      name='Test category1', currency='CHF', type=models.Account.Types.VIRTUAL).id
    self.v_account2_id = profile.AddAccount(
      name='Test category2', currency='CHF', type=models.Account.Types.VIRTUAL).id


class AddTransactionTestCase(BaseTransactionTestCase):
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

  def testOnlySourceAccountIsSpecified(self):
    self.assertRaises(
      ValueError, transactions.AddTransaction, self.profile_id, 10.0, self.now,
      source_account_id=self.account1_id)

  def testNoAccountIdIsSpecified(self):
    self.assertRaises(
      ValueError, transactions.AddTransaction, self.profile_id, 10.0, self.now)


class UpdateTransactionTestCase(BaseTransactionTestCase):
  def setUp(self):
    super(UpdateTransactionTestCase, self).setUp()

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


class DeleteTransactionsTestCase(BaseTransactionTestCase):
  def testNormal(self):
    transaction_id1 = transactions.AddTransaction(
      self.profile_id, 10.0, self.now, dest_account_id=self.account1_id).key.id()
    transaction_id2 = transactions.AddTransaction(
      self.profile_id, 100.0, self.now,
      source_account_id=self.account1_id, dest_account_id=self.account2_id).key.id()

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(-90.0, profile.GetAccountById(self.account1_id).balance)
    self.assertAlmostEqual(66.66666666, profile.GetAccountById(self.account2_id).balance)

    transactions.DeleteTransactions(
      self.profile_id, [transaction_id1, transaction_id2])

    profile = models.Profile.GetActive(self.visitor_id)
    self.assertAlmostEqual(0.0, profile.GetAccountById(self.account1_id).balance)
    self.assertAlmostEqual(0.0, profile.GetAccountById(self.account2_id).balance)

    self.assertIsNone(models.Transaction.Get(self.profile_id, transaction_id1))
    self.assertIsNone(models.Transaction.Get(self.profile_id, transaction_id2))

from datetime import datetime
from google.appengine.ext import ndb
from datastore import models

def CalculateUnplannedExpensesAndIncome(budget, transactions):
  unplanned_income = 0
  unplanned_expenses = 0
  budget_transaction_ids = GetTransactionIdsOfBudget(budget)
  for transaction in transactions:
    if transaction.key.id() in budget_transaction_ids:
        if transaction.amount > 0:
          unplanned_expenses += transaction.amount
        else:
          unplanned_income -= transaction.amount

  return unplanned_income, unplanned_expenses


def GetTransactionIdsOfBudget(budget):
  return set((i.transaction_id for i in budget.items))


def GetBudget(profile, str_date):
  budget_date = datetime.now()
  if str_date:
    budget_date = models.Budget.ParseDate(str_date)

  budget_key = ndb.Key(models.Budget, models.Budget.DateToStr(budget_date),
                       parent=profile.key)
  budget = budget_key.get()
  if not budget:
    budget = models.Budget(parent=profile.key,
                           id=models.Budget.DateToStr(budget_date),
                           date=budget_date)

  return budget


def GetBudgetViewItems(profile, budget):
  budget_view_items = []
  for item in budget.items:
    if item.category_id is not None:
      budget_view_items.append({
        'name': profile.categories[item.category_id].name,
        'category_id': item.category_id,
        'amount': item.planned_amount
      })

  return budget_view_items

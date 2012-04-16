from common import CommonHandler
from datastore import  lookup
from util import  budget_util


class MainPage(CommonHandler):
  def HandleGet(self):
    budget = budget_util.GetBudget(self.profile, self.request.get('date'))

    transactions = lookup.GetTransactionsForBudget(self.profile, budget)
    unplanned_income, unplanned_expenses = (
        budget_util.CalculateUnplannedExpensesAndIncome(
            budget, transactions))

    total_balance = sum([a.balance for a in self.profile.accounts])
    categories_total_balance = sum([c.balance for c in self.profile.categories])

    budget_view_items = budget_util.GetBudgetViewItems(self.profile, budget)
    common_savings = 9000
    max_expense = 0
    for item in budget.items:
      if item.category_id is not None:
        common_savings -= item.planned_amount
        max_expense = max(max_expense, item.planned_amount)

    budget_view_items.append({
      'name': 'Other expenses',
      'amount': unplanned_expenses
    })
    common_savings -= unplanned_expenses
    max_expense = max(max_expense, common_savings)

    template_values = {
      'total_balance': total_balance,
      'categories_total_balance': categories_total_balance,
      'budget_items': budget_view_items,
      'common_savings': common_savings,
      'max_expense': max_expense
    }

    self.WriteToTemplate('templates/index.html', template_values)


class AdminPage(CommonHandler):
  def HandleGet(self):

    template_values = {
      'transactions': lookup.GetAllTransactions(self.profile),
      'currency_rates': lookup.GetLatestCurrencyRates()
    }

    self.WriteToTemplate('templates/admin.html', template_values)

from common_handlers import CommonHandler
from datastore import lookup
from util import budget_util


class EditBudgetPage(CommonHandler):
  def HandleGet(self):
    budget = budget_util.GetBudget(self.profile, self.request.get('date'))

    transactions = lookup.GetTransactionsForBudget(self.profile, budget)
    unplanned_income, unplanned_expenses = (
        budget_util.CalculateUnplannedExpensesAndIncome(
            budget, transactions))

    template_values = {
      'budget': budget,
      'unplanned_income': unplanned_income,
      'unplanned_expenses': unplanned_expenses
    }

    self.WriteToTemplate('templates/planning/edit_budget.html', template_values)

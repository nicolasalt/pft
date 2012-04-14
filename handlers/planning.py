from common_handlers import CommonHandler
from datastore import lookup, models
from util import budget_util, parse, ndb_json


class DoEditBudgetCategory(CommonHandler):
  def HandlePost(self):
    item_id = parse.ParseInt(self.request.get('item_id'))
    amount = parse.ParseFloat(self.request.get('amount'))
    category_id = parse.ParseInt(self.request.get('category_id'))
    budget = budget_util.GetBudget(self.profile, self.request.get('date'))
    delete = self.request.get('delete') == '1'

    if delete:
      budget.items = budget.items[:item_id] + budget.items[item_id + 1:]
    else:
      if item_id is not None:
        budget_item = budget.items[item_id]
      else:
        budget_item = models.BudgetItem()
        budget.items.append(budget_item)

      budget_item.category_id = category_id
      budget_item.planned_amount = amount

    budget.put()

    self.response.set_status(200)


class EditBudgetPage(CommonHandler):
  def HandleGet(self):
    budget = budget_util.GetBudget(self.profile, self.request.get('date'))

    transactions = lookup.GetTransactionsForBudget(self.profile, budget)
    unplanned_income, unplanned_expenses = (
        budget_util.CalculateUnplannedExpensesAndIncome(
            budget, transactions))

    budget_view_items = []
    for item in budget.items:
      if item.category_id is not None:
        budget_view_items.append({
          'name': self.profile.categories[item.category_id].name,
          'amount': item.planned_amount
        })

    template_values = {
      'budget': budget,
      'budget_items': budget_util.GetBudgetViewItems(self.profile, budget),
      'budget_items_json': [ndb_json.encode(i) for i in budget.items],
      'unplanned_income': unplanned_income,
      'unplanned_expenses': unplanned_expenses
    }

    self.WriteToTemplate('templates/planning/edit_budget.html', template_values)

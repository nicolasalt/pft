
def CalculateExpensesAndIncome(budget, transactions):
  cat_id_to_planned_expense = dict(
    [(exp.category_id, exp.planned_value) for exp in budget.expenses])

  total_income = 0
  total_expenses = 0
  for transaction in transactions:
    if transaction.category_id:
      if (not transaction.category_id in cat_id_to_planned_expense or
          cat_id_to_planned_expense[transaction.category_id] is not None):
        if transaction.amount > 0:
          total_expenses += transaction.amount
        else:
          total_income -= transaction.amount

  return total_income, total_expenses

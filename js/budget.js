
pft.DeleteBudgetItem = function(budgetDate, itemId) {
  pft.SaveBudgetItem(budgetDate, itemId, true);
};


pft.EditBudgetItem = function(budgetDate, itemId) {
  var item = pft.state.GetBudgetItem(itemId);
  if (!item) {
    item = {
      'planned_amount': '',
      'category_id': '0'
    };
  }
  $('#edit-budget-item-amount').val(item['planned_amount']);
  $('#edit-budget-item-category').val(item['category_id']);
  $('#edit-budget-item-dialog').dialog({
      resizable: false,
      title: 'Add new budget category',
      buttons: {
        'Save': function() {
          pft.SaveBudgetItem(budgetDate, itemId);
        },
        'Cancel': function() {
          $(this).dialog('close');
        }
      }
  });
};


pft.SaveBudgetItem = function(budgetDate, itemId, opt_delete){
  var data = {
    'date': budgetDate,
    'amount': $('#edit-budget-item-amount').val(),
    'category_id': $('#edit-budget-item-category').val()
  };
  if (itemId) {
    data['item_id'] = itemId;
  }
  if (opt_delete) {
    data['delete'] = '1';
  }

  $.post('/do/edit_budget_category', data).success(function() {
    window.location.reload();
  });
  $('#edit-budget-item-dialog').dialog('close');
};

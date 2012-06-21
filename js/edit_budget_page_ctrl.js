
pft.EditBudgetPageCtrl = function($scope, $resource, $routeParams) {
  $scope.budgetDate = $routeParams.budgetDate;

  // TODO: extract request to the API service.
  var getBudgetRequest = $resource('/api/get_budget', {}, {
    query: {method:'GET'}
  });
  $scope.updateBudget = function () {
    var args = {};
    if ($scope.budgetDate != null) args['date'] = $scope.budgetDate;
    $scope.budgetData = getBudgetRequest.get(args, function() {
      $scope.budgetFormatted = angular.toJson(eval($scope.budgetData), true);
    });
  };
  $scope.updateBudget();

  // TODO: extract request to the API service.
  var getTransactionsRequest = $resource('/api/get_transactions', {}, {
    query: {method:'GET'}
  });
  $scope.updateTransactions = function () {
    var args = {};
    if ($scope.budgetDate != null) args['budget_date'] = $scope.budgetDate;
    $scope.transactionData = getTransactionsRequest.get(
        args,
        function() {
          $scope.transactionsFormatted = angular.toJson(eval($scope.transactionData), true);
          $scope.transactions = $scope.transactionData.transactions;
        });
  };
  $scope.updateTransactions();

  $scope.editBudgetItem = function (item, itemId) {
    if (!item) {
      item = {
        'planned_amount': '',
        'category_id': '0'
      };
    }
    $scope.budgetCategoryPlannedAmount = item['planned_amount'];
    $scope.budgetCategory = $scope.profile.categories[item['category_id']];
    $('#edit-budget-item-dialog').dialog({
        resizable: false,
        title: 'Add new budget category',
        buttons: {
          'Save': function() {
            $scope.saveBudgetItem(itemId);
          },
          'Cancel': function() {
            $(this).dialog('close');
          }
        }
    });
  };

  $scope.deleteBudgetItem = function (itemId) {
    $scope.saveBudgetItem(itemId, true);
  };

  $scope.saveBudgetItem = function (itemId, opt_delete) {
    var data = {
      'date': $scope.budgetDate,
      'amount': $scope.budgetCategoryPlannedAmount,
      'category_id': $scope.budgetCategory.category_id
    };
    if (itemId != null) {
      data['item_id'] = itemId;
    }
    if (opt_delete) {
      data['delete'] = '1';
    }

    $.post('/do/edit_budget_category', data).success(function() {
      $scope.updateBudget();
    });
    $('#edit-budget-item-dialog').dialog('close');
  };
};

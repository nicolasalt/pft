
pft.TransactionsPageCtrl = function($scope, $resource, $routeParams) {
  $scope.categoryId = $routeParams.categoryId;
  $scope.accountId = $routeParams.accountId;
  $scope.budgetDate = $routeParams.budgetDate;

  $scope.category = $scope.profile.categories[$scope.categoryId];
  $scope.account = $scope.profile.accounts[$scope.accountId];

  // TODO: extract request to the API service.
//  var getBudgetRequest = $resource('/api/get_budget', {}, {
//    query: {method:'GET'}
//  });
//  $scope.updateBudget = function () {
//    $scope.budget = getBudgetRequest.get(null, function() {
//      $scope.budgetFormatted = angular.toJson(eval($scope.budget), true);
//    });
//  };
//  $scope.updateBudget();

  var getTransactionsRequest = $resource('/api/get_transactions', {}, {
    query: {method:'GET'}
  });
  $scope.updateTransactions = function () {
    var transactionArgs = {};
    if ($scope.categoryId != null) transactionArgs['category_id'] = $scope.categoryId;
    if ($scope.accountId != null) transactionArgs['account_id'] = $scope.accountId;
    if ($scope.budgetDate != null) transactionArgs['budget_date'] = $scope.budgetDate;
    $scope.transactionData = getTransactionsRequest.get(
        transactionArgs,
        function() {
          $scope.transactionsFormatted = angular.toJson(eval($scope.transactionData), true);
          $scope.transactions = $scope.transactionData.transactions;
        });
  };
  $scope.updateTransactions();
};


pft.TransactionsPageCtrl = function($scope, $resource, $routeParams) {
  $scope.categoryId = $routeParams.categoryId;

  $scope.category = $scope.profile.categories[$scope.categoryId];

  // TODO: extract request to the API service.
  var getBudgetRequest = $resource('/api/get_budget', {}, {
    query: {method:'GET'}
  });
  $scope.updateBudget = function () {
    $scope.budget = getBudgetRequest.get(null, function() {
      $scope.budgetFormatted = angular.toJson(eval($scope.budget), true);
    });
  };
  $scope.updateBudget();

  var getTransactionsRequest = $resource('/api/get_transactions', {}, {
    query: {method:'GET'}
  });
  $scope.updateTransactions = function () {
    $scope.transactionData = getTransactionsRequest.get(
        {'category_id': $scope.categoryId},
        function() {
          $scope.transactionsFormatted = angular.toJson(eval($scope.transactionData), true);
          $scope.transactions = $scope.transactionData.transactions;
        });
  };
  $scope.updateTransactions();
};

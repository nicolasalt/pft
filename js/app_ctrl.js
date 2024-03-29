
pft.mainModule = angular.module('pftApp', ['ngResource', 'pft.directives']).
    config(['$routeProvider', function($routeProvider) {
      $routeProvider.
          when('/transactions/budget_date=:budgetDate',
               {templateUrl: 'transactions_page.html', controller: pft.TransactionsPageCtrl}).
          when('/transactions/category_id=:categoryId',
               {templateUrl: 'transactions_page.html', controller: pft.TransactionsPageCtrl}).
          when('/transactions/account_id=:accountId',
               {templateUrl: 'transactions_page.html', controller: pft.TransactionsPageCtrl}).
          when('/transactions',
               {templateUrl: 'transactions_page.html', controller: pft.TransactionsPageCtrl}).
          when('/edit_budget/budget_date=:budgetDate',
               {templateUrl: 'edit_budget_page.html', controller: pft.EditBudgetPageCtrl}).
          when('/edit_budget',
               {templateUrl: 'edit_budget_page.html', controller: pft.EditBudgetPageCtrl}).
          when('/import_from_file',
               {templateUrl: 'import_from_file_page.html', controller: pft.ImportFromFilePageCtrl}).
          when('/edit_imported_file/id=:importedFileId',
               {templateUrl: 'edit_imported_file_page.html',
                controller: pft.EditImportedFilePageCtrl}).
          otherwise({templateUrl: 'main_page.html', controller: pft.MainPageCtrl});
    }]);


pft.AppCtrl = function($scope, $resource, $location) {
  var getProfileRequest = $resource('/api/get_profile', {}, {
    query: {method:'GET'}
  });

  $scope.profile = null;

  $scope.updateProfile = function () {
    $scope.profileData = getProfileRequest.get(null, function() {
      $scope.profileDataFormatted = angular.toJson(eval($scope.profileData), true);
      $scope.profile = $scope.profileData.profile;
    });
  };
  $scope.updateProfile();

  $scope.openTransactionDialog = function (opt_transactionId) {
    pft.TransactionDialog.Dialog.open(opt_transactionId);
  };

  $scope.openImportFromFile = function () {
    $location.path('/import_from_file');
  };
};

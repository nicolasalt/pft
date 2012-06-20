
pft.mainModule = angular.module('pftApp', ['ngResource', 'pft.directives']).
    config(['$routeProvider', function($routeProvider) {
      $routeProvider.
          when('/transactions/category_id=:categoryId',
               {templateUrl: 'transactions_page.html', controller: pft.TransactionsPageCtrl}).
          otherwise({templateUrl: 'main_page.html', controller: pft.MainPageCtrl});
    }]);


pft.AppCtrl = function($scope, $resource) {
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
};


pft.mainModule = angular.module('pftApp', ['ngResource', 'pft.directives']);

pft.AppCtrl = function($scope, $resource) {
  $scope.name = 'Nikolay';

  var api = $resource('/api/get_profile', {}, {
    query: {method:'GET'}
  });

  $scope.profileData = api.get(null, function() {
    $scope.profileDataFormatted = angular.toJson(eval($scope.profileData), true);
  });
};

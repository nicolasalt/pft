
pft.module = angular.module('pftApp', ['ngResource']);

pft.AppCtrl = function($scope, $resource) {
  $scope.name = 'Nikolay';

  var api = $resource('/api/get_profile', {}, {
    query: {method:'GET'}
  });

  $scope.profileData = api.get();
};

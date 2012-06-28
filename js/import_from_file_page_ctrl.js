
pft.ImportFromFilePageCtrl = function($scope, $resource, $routeParams) {
  $scope.submitTransactionsForm = function () {
    $('#add_transactions_form').submit();
  };

  var getImportedFilesRequest = $resource('/api/get_imported_file_descriptions', {}, {
    query: {method:'GET'}
  });

  $scope.importedFileDescriptions = null;

  $scope.updateImportedFileDescriptions = function () {
    $scope.importedFileDescriptionsData = getImportedFilesRequest.get(null, function() {
      $scope.importedFileDescriptions =
          $scope.importedFileDescriptionsData.imported_file_descriptions;
    });
  };
  $scope.updateImportedFileDescriptions();
};

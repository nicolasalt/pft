
pft.EditImportedFilePageCtrl = function($scope, $resource, $routeParams, $http) {
  $scope.importedFileId = $routeParams.importedFileId;

  $scope.dialog = new pft.SplitTransactionDialog();

  var getImportedFileRequest = $resource('/api/get_imported_file', {}, {
    query: {method:'GET'}
  });

  $scope.importedFile = null;

  $scope.updateImportedFileDescriptions = function () {
    $scope.importedFileData = getImportedFileRequest.get(
        {'id': $scope.importedFileId}, function() {
      $scope.importedFile =
          $scope.importedFileData.imported_file;
      $scope.account = $scope.profile.accounts[$scope.importedFile.account_id];
    });
  };
  $scope.updateImportedFileDescriptions();

  $scope.applySelectedSchema = function () {
    $.post('/api/do/apply_parse_schema_to_import_file', {
          'id': $scope.importedFile.id,
          'schema': $scope.schema['schema']}).success(
        $scope.updateImportedFileDescriptions);
  };

  $scope.addParseSchema = function () {
    $.post('/api/do/add_parse_schema', {
          'name': $scope.schemaName,
          'schema': $scope.schemaToAdd}).success(
        $scope.updateProfile);
  };
};

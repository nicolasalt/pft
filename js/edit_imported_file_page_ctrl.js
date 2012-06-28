
pft.EditImportedFilePageCtrl = function($scope, $resource, $routeParams) {
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

  var applyParseSchemaRequest = $resource('/api/apply_parse_schema_to_import_file', {}, {
    query: {method:'POST'}
  });
  $scope.applySelectedSchema = function () {
    applyParseSchemaRequest.post({
        'id': $scope.importedFile.id,
        'schema': $scope.schema},
      $scope.updateImportedFileDescriptions);
  };

  var addParseSchemaRequest = $resource('/api/add_parse_schema', {}, {
    query: {method:'POST'}
  });
  $scope.addParseSchema = function () {
    addParseSchemaRequest.post({
        'name': $scope.schemaName,
        'schema': $scope.schemaToAdd},
      $scope.updateImportedFileDescriptions);
  };
};

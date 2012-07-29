
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


  $scope.currentTransactionIndex = 0;
  $scope.getCurrentTransaction = function() {
    if (!$scope.importedFile || !$scope.importedFile.parsed_transactions) return null;

    return $scope.importedFile.parsed_transactions[$scope.currentTransactionIndex];
  };
  $scope.nextTransaction = function () {
    if (!$scope.importedFile || !$scope.importedFile.parsed_transactions) return;

    if ($scope.currentTransactionIndex < $scope.importedFile.parsed_transactions.length - 1) {
      $scope.currentTransactionIndex++;
    }
  };
  $scope.previousTransaction = function () {
    if (!$scope.importedFile || !$scope.importedFile.parsed_transactions) return;

    if ($scope.currentTransactionIndex > 0) {
      $scope.currentTransactionIndex--;
    }
  };
  $scope.switchToTransaction = function (tIndex) {
    $scope.currentTransactionIndex = tIndex;
  };
  $scope.resolveTransaction = function (category, opt_drop) {
    var catToAmount = {};
    catToAmount[category.category_id] = $scope.getCurrentTransaction().amount;

    var data = {
      'imported_file_id': $scope.importedFile.id,
      'transaction_index': $scope.currentTransactionIndex};

    if (opt_drop) {
      data['drop'] = '1';
    } else {
      var categoriesToSend = [];
      var amountsToSend = [];
      for (var catId in catToAmount) {
        categoriesToSend.push(catId);
        amountsToSend.push(catToAmount[catId]);
      }

      data['categories'] = categoriesToSend.join(',');
      data['amounts'] = amountsToSend.join(',');
    }

    $.post('/do/resolve_parsed_transaction', data);
    // TODO: update view.
  };
};

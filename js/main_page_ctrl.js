
pft.MainPageCtrl = function($scope, $resource) {
  var getBudgetRequest = $resource('/api/get_budget', {}, {
    query: {method:'GET'}
  });
  $scope.updateBudget = function () {
    $scope.budget = getBudgetRequest.get(null, function() {
      $scope.budgetFormatted = angular.toJson(eval($scope.budget), true);
    });
  };
  $scope.updateBudget();

  $scope.openEditCategoryDialog = function(opt_catId) {
    var category = $scope.profile.categories[opt_catId];

    var title = 'Edit category';
    if (opt_catId == undefined) {
      category = {
        'name': '',
        'balance': ''
      };
      title = 'Add new category';
    }
    $('#edit-category-name').val(category['name']);
    $('#edit-category-balance').val(category['balance']);
    $('#edit-category-dialog').dialog({
        resizable: false,
        title: title,
        buttons: {
          'Save': function() {
            $scope.saveCategory(opt_catId);
          },
          'Cancel': function() {
            $(this).dialog('close');
          }
        }
    });
  };

  $scope.saveCategory = function(categoryId, opt_delete){
    var data = {
      'name': $('#edit-category-name').val()
    };
    var balance = $('#edit-category-balance').val();
    if (balance) {
      data['balance'] = balance;
    }
    if (categoryId != null) {
      data['category_id'] = categoryId;
    }
    if (opt_delete) {
      data['delete'] = '1';
    }

    $.post('/do/edit_category', data).success(function() {
      $scope.updateProfile();
    });
    $('#edit-category-dialog').dialog('close');
  };

  $scope.openEditAccountDialog = function(opt_accountId) {
    var account = $scope.profile.accounts[opt_accountId];

    var title = 'Edit account';
    if (opt_accountId == undefined) {
      account = {
        'name': '',
        'balance': '',
        'currency': 'USD'
      };
      title = 'Add new account';
    }
    $('#edit-account-name').val(account['name']);
    $('#edit-account-balance').val(account['balance']);
    $('#edit-account-currency').val(account['currency']);
    $('#edit-account-dialog').dialog({
        resizable: false,
        title: title,
        buttons: {
          'Save': function() {
            $scope.saveAccount(opt_accountId);
          },
          'Cancel': function() {
            $(this).dialog('close');
          }
        }
    });
  };

  $scope.saveAccount = function(opt_accountId, opt_delete){
    var data = {
      'name': $('#edit-account-name').val(),
      'currency': $('#edit-account-currency').val()
    };
    var balance = $('#edit-account-balance').val();
    if (balance) {
      data['balance'] = balance;
    }
    if (opt_accountId != null) {
      data['account_id'] = opt_accountId;
    }
    if (opt_delete) {
      data['delete'] = '1';
    }

    $.post('/do/edit_account', data).success(function() {
      $scope.updateProfile();
    });
    $('#edit-account-dialog').dialog('close');
  };
};

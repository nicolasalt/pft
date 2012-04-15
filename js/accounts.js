pft.accounts = {};


pft.accounts.DeleteAccount = function(accountId) {
  // TODO: implement delete
  //pft.accounts.SaveAccount(accountId, true);
};


pft.accounts.EditAccount = function(accountId) {
  var account = pft.state.GetAccount(accountId);
  var title = 'Edit account';
  if (accountId == '') {
    account = {
      'name': '',
      'balance': '',
      'currency': '$'
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
          pft.accounts.SaveAccount(accountId);
        },
        'Cancel': function() {
          $(this).dialog('close');
        }
      }
  });
};


pft.accounts.SaveAccount = function(accountId, opt_delete){
  var data = {
    'name': $('#edit-account-name').val(),
    'currency': $('#edit-account-currency').val()
  };
  var balance = $('#edit-account-balance').val();
  if (balance) {
    data['balance'] = balance;
  }
  if (accountId) {
    data['account_id'] = accountId;
  }
  if (opt_delete) {
    data['delete'] = '1';
  }

  $.post('/do/edit_account', data).success(function() {
    window.location.reload();
  });
  $('#edit-account-dialog').dialog('close');
};


$('[account_id]').live('click', function(){
  pft.accounts.EditAccount(
      $(this).attr('account_id'));
});
$('[delete_account_id]').live('click', function(){
  pft.accounts.DeleteAccount(
      $(this).attr('delete_account_id'));
});

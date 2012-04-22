pft.AccountTransferDialog = function() {
  this.element_ = $('#account-transfer-dialog');
  this.element_.dialog({
    autoOpen: false,
    resizable: false,
    width: 600,
    buttons: {
      'Save': this.handleSaveButtonClicked_.bind(this),
      'Cancel': function() {
        $(this).dialog('close');
      }
    }
  });

  this.datePicker_ = $('#account-transfer-dialog-datepicker');
  this.datePicker_.datepicker({
    inline: true,
    dateFormat: 'dd.mm.yy'
  });

  this.amountInput_ = $('#account-transfer-dialog-amount');

  this.errorDiv_ = $('#account-transfer-dialog-error');

  $('#account-transfer-dialog-source-accounts').buttonset();
  $('#account-transfer-dialog-dest-accounts').buttonset();
};


pft.AccountTransferDialog.prototype.handleSaveButtonClicked_ = function() {
  var data = {
    'amount': this.amountInput_.val(),
    'account_id': this.element_.find('[source_account_id]:checked').val(),
    'dest_account_id': this.element_.find('[dest_account_id]:checked').val(),
    'date': $.datepicker.formatDate('dd.mm.yy',
        this.datePicker_.datepicker('getDate'))
  };
  $.post('/do/edit_transaction', data).success(function() {
    window.location.reload();
  });
  this.element_.dialog('close');
};


pft.AccountTransferDialog.prototype.open =
    function(sourceAccountId, destAccountId) {
  var date = new Date();
  this.datePicker_.datepicker('setDate',new Date());
  this.amountInput_.val('');

  this.datePicker_.datepicker('setDate', date);
  this.element_.dialog('option', 'title',
                       $.datepicker.formatDate('dd.mm.yy', date));
  this.errorDiv_.text('');

  this.element_.find('[for="tdas-' + sourceAccountId + '"]').click();
  this.element_.find('[source_account_id="' + sourceAccountId + '"]').
      prop('checked', true);

  this.element_.find('[for="tdad-' + destAccountId + '"]').click();
  this.element_.find('[dest_account_id="' + destAccountId + '"]').
      prop('checked', true);

  this.element_.dialog('open');
  this.amountInput_.focus();
};


$(function() {
  pft.AccountTransferDialog.Dialog = new pft.AccountTransferDialog();
});

pft.TransactionDialog = function() {
  this.element_ = $('#transaction-dialog');
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

  // Form for easier radio button state access.
  this.form_ = $('#transaction-dialog-form');

  this.datePicker_ = $('#transaction-dialog-datepicker');
  this.datePicker_.datepicker({
    inline: true,
    dateFormat: 'dd.mm.yy'
  });

  this.inputArea_ = $('#transaction-dialog-input-area');

  $('#transaction-dialog-categories').buttonset();
  $('#transaction-dialog-accounts').buttonset();

  this.transactionId_ = null;
};

pft.TransactionDialog.prototype.handleSaveButtonClicked_ = function() {
  var data = {
    'transaction_id': this.transactionId_ || '',
    'amount_and_description': this.inputArea_.val(),
    'category_id': this.element_.find('[category_id]:checked').val(),
    'account_id': this.element_.find('[account_id]:checked').val(),
    'date': this.datePicker_.datepicker('getDate')
  };
  alert(JSON.stringify(data));
};

pft.TransactionDialog.prototype.open = function(transactionId) {
  this.transactionId_ = transactionId;

  var transaction = pft.state.GetTransaction(transactionId);
  if (!transaction) {
    transaction = {
      'amount': '',
      'description': '',
      'date': new Date()
    };
  }

  this.inputArea_.val(
      transaction['amount'] + ' ' + transaction['description']);
  this.datePicker_.datepicker('setDate', transaction['date']);
  var categoryId = transaction['category_id'] == null ? '' :
      transaction['category_id'];
  var account_id = transaction['account_id'] || 0;
  this.element_.find('[for="tdc-' + categoryId + '"]').click();
  this.element_.find('[for="tda-' + account_id + '"]').click();

  this.element_.dialog('option', 'title', transaction['date']);
  this.element_.dialog('open');
  this.inputArea_.focus();
};

$(function() {
  pft.TransactionDialog.Dialog = new pft.TransactionDialog();
  $('[transaction_id]').live('click', function() {
    pft.TransactionDialog.Dialog.open($(this).attr('transaction_id'));
  });
});

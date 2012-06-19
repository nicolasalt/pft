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

  this.datePicker_ = $('#transaction-dialog-datepicker');
  this.datePicker_.datepicker({
    inline: true,
    dateFormat: 'dd.mm.yy'
  });

  this.inputArea_ = $('#transaction-dialog-input-area');

  this.errorDiv_ = $('#transaction-dialog-error');

//  $('#transaction-dialog-categories').buttonset();
//  $('#transaction-dialog-accounts').buttonset();

  this.transactionId_ = null;
};


pft.TransactionDialog.prototype.handleSaveButtonClicked_ = function() {
  var amountAndDescription = this.inputArea_.val();
  var firstSpaceIndex = amountAndDescription.search(' ');
  if (firstSpaceIndex < 0) {
    this.errorDiv_.text(
        'No space found in the text. The text format should be: ' +
        '"number text", e.g. "12.5 tasty pineapples"');
    return;
  }
  var amount = parseFloat(amountAndDescription.slice(0, firstSpaceIndex));
  if (!amount) {
    this.errorDiv_.text(
        'The first word is not a valid number. The text format should be: ' +
        '"number text", e.g. "12.5 tasty pineapples"');
    return;
  }
  var description = amountAndDescription.slice(firstSpaceIndex + 1);
  var data = {
    'transaction_id': this.transactionId_ || '',
    'amount': amount,
    'description': description,
    'category_id': this.element_.find('[category_id]:checked').val(),
    'account_id': this.element_.find('[account_id]:checked').val(),
    'date': $.datepicker.formatDate('dd.mm.yy',
        this.datePicker_.datepicker('getDate'))
  };
  $.post('/do/edit_transaction', data).success(function() {
    window.location.reload();
  });
  this.element_.dialog('close');
};


pft.TransactionDialog.prototype.open = function(transactionId) {
  this.transactionId_ = transactionId;

  var transaction = pft.state.GetTransaction(transactionId);
  var date = new Date();
  if (!transaction) {
    transaction = {};
    this.datePicker_.datepicker('setDate', transaction['date']);
    this.inputArea_.val('');
  } else {
    date = $.datepicker.parseDate(
        'yy-mm-dd', transaction['date'].substr(0, 10));
    this.inputArea_.val(transaction['amount'] + ' ' +
        transaction['description']);
  }

  this.datePicker_.datepicker('setDate', date);
  this.element_.dialog('option', 'title',
                       $.datepicker.formatDate('dd.mm.yy', date));
  this.errorDiv_.text('');

  var categoryId = transaction['category_id'] == null ? '' :
      transaction['category_id'];
  this.element_.find('[for="tdc-' + categoryId + '"]').click();
  this.element_.find('[category_id="' + categoryId + '"]').
      prop('checked', true);

  var accountId = transaction['account_id'] || 0;
  this.element_.find('[for="tda-' + accountId + '"]').click();
  this.element_.find('[account_id="' + accountId + '"]').
      prop('checked', true);

  this.element_.dialog('open');
  this.inputArea_.focus();
};


$(function() {
  pft.TransactionDialog.Dialog = new pft.TransactionDialog();
});

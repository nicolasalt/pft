pft.TransactionDialog = function() {
  this.element_ = $('#transaction-dialog');
  this.element_.dialog({
    autoOpen: false,
    resizable: false,
    width: 600,
    buttons: {
      'Save': function() {
        $(this).dialog('close');
      },
      'Cancel': function() {
        $(this).dialog('close');
      }
    }
  });

  // Form for easier radio button state access.
  this.form_ = $('#transaction-form');

  this.datePicker_ = $('#transaction-dialog-datepicker');
  this.datePicker_.datepicker({
    inline: true,
    dateFormat: 'dd.mm.yy'
  });

  this.inputArea_ = $('#transaction-dialog-input-area');

  $('#transaction-dialog-categories').buttonset();
  $('#transaction-dialog-accounts').buttonset();
};

pft.TransactionDialog.prototype.open = function(transaction_id) {
  var transaction = pft.state.GetTransaction(transaction_id);
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
  this.element_.find(['category_id=' + transaction['category_id']]).
      attr('checked', true);
  this.element_.find(['account_id=' + transaction['account_id']]).
      attr('checked', true);
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

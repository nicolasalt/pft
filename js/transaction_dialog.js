pft.transactionDialog = {};

pft.transactionDialog.open = function(transaction_id) {
  var transaction = pft.state.GetTransaction(transaction_id);
  if (!transaction) {
    transaction = {
      'amount': '',
      'description': '',
      'date': new Date(),
      'category_id': null
    };
  }

  $('#transaction-dialog-input-area').val(
      transaction['amount'] + ' ' + transaction['description']);
  $('#transaction-dialog-datepicker').datepicker('setDate', transaction['date']);
  $('#transaction-dialog-category-' + transaction['category_id']).attr('checked', true);
  $('#transaction-dialog').dialog('option', 'title', transaction['date']);
  $('#transaction-dialog').dialog('open');
  $('#transaction-dialog-input-area').focus();

};

$(function() {
  $('#transaction-dialog').dialog({
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
  $('#transaction-dialog-datepicker').datepicker({
    inline: true,
    dateFormat: 'dd.mm.yy'
  });
  $('#transaction-dialog-categories').buttonset();
  $('#transaction-dialog-accounts').buttonset();

  $('[transaction_id]').live('click', function() {
    pft.transactionDialog.open($(this).attr('transaction_id'));
  });
});

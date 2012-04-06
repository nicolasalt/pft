pf.transactionDialog = {};

pf.transactionDialog.open = function(transaction_id) {
  var transaction = pf.state.GetTransaction(transaction_id);
  if (!transaction) return;

  $('#transaction-dialog-amount').val(transaction['amount']);
  $('#transaction-dialog-description').val(transaction['description']);
  $('#transaction-dialog').dialog('open');
};

$(function() {
  $('#transaction-dialog').dialog({
    autoOpen: false
  });
  $('#transaction-dialog-datepicker').datepicker({
    inline: true
  });
  $('#transaction-dialog-categories').buttonset();


  $('[transaction_id]').live('click', function() {
    pf.transactionDialog.open($(this).attr('transaction_id'));
  });
});

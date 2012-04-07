pft.transactionDialog = {};

pft.transactionDialog.open = function(transaction_id) {
  var transaction = pft.state.GetTransaction(transaction_id);
  if (!transaction) return;

  $('#transaction-dialog-description').val(transaction['description']);
  $('#transaction-dialog-datepicker').datepicker('setDate', transaction['date']);
  $('#transaction-dialog-category-' + transaction['category_id']).attr('checked', true);
  $('#transaction-dialog-amount').val(transaction['amount']);
  $('#transaction-dialog').dialog('option', 'title', transaction['date']);
  $('#transaction-dialog').dialog('open');
  $('#transaction-dialog-amount').focus();
};

$(function() {
  $('#transaction-dialog').dialog({
    autoOpen: false,
    resizable: false,
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


  $('[transaction_id]').live('click', function() {
    pft.transactionDialog.open($(this).attr('transaction_id'));
  });
});

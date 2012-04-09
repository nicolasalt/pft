

pft.ParsedTransactionProcessor = function(element, transactionIndex) {
  this.element_ = element;

  this.transactionIndex_ = transactionIndex;

  this.transaction_ = pft.state.GetImportedTransaction(transactionIndex);

  this.selectors_ = [];
  this.createSelector_(null, 'No category');
  for (var catId in pft.state.GetCategories()) {
    var category = pft.state.GetCategory(catId);
    this.createSelector_(catId, category['name']);
  }

  this.dropTransactionSelector_ = $('<a/>').attr('href', 'javascript:void(0)').
      addClass('selector drop_button').text('Drop');
  this.dropTransactionSelector_.click(this.handleCategoryClicked.bind(
      this, null, this.dropTransactionSelector_, true));
  this.element_.append(this.dropTransactionSelector_);

  this.splitTransactionSelector_ = $('<a/>').attr('href', 'javascript:void(0)').
      addClass('selector').text('Split');
  this.splitTransactionSelector_.click(
      this.handleSplitButtonClicked_.bind(this));
  this.element_.append(this.splitTransactionSelector_);

  this.cancelButton_ = $('<a/>').attr('href', 'javascript:void()').
      addClass('cancel_button').text('Change');
  this.cancelButton_.click(this.handleCancelButtonClicked.bind(this));
  this.element_.append(this.cancelButton_);

  amplify.subscribe(pft.SplitTransactionDialog.Events.SPLIT,
                    this.handleSplitPerformed_.bind(this));
};


pft.ParsedTransactionProcessor.prototype.handleSplitPerformed_ =
    function(transactionIndex, catToAmount) {
  if (this.transactionIndex_ != transactionIndex) return;

  alert(transactionIndex + '' + JSON.stringify(catToAmount));
};


pft.ParsedTransactionProcessor.prototype.handleSplitButtonClicked_ =
    function() {
  pft.SplitTransactionDialog.Dialog.open(
      this.transactionIndex_, this.transaction_['amount']);
};


pft.ParsedTransactionProcessor.prototype.createSelector_ =
    function(catId, catName) {
  var categorySelector = $('<a/>').attr('href', 'javascript:void(0)').
      addClass('selector').text(catName);
  categorySelector.click(this.handleCategoryClicked.bind(
      this, catId, categorySelector, false));
  this.element_.append(categorySelector);
  this.selectors_.push(categorySelector);
};


pft.ParsedTransactionProcessor.IMPORTED_FILE_ID = null;


pft.ParsedTransactionProcessor.prototype.handleCategoryClicked =
    function(catId, selector, drop) {
  this.element_.parent().addClass('processed');
  selector.addClass('selected');
  var data = {
    'imported_file_id': pft.ParsedTransactionProcessor.IMPORTED_FILE_ID,
    'transaction_index': this.transactionIndex_,
    'category_id': catId || ''};
  if (drop) {
    data['drop'] = '1';
  }
  $.post('/do/resolve_parsed_transaction', data);
};


pft.ParsedTransactionProcessor.prototype.handleCancelButtonClicked =
    function() {
  this.element_.parent().removeClass('processed');
  this.element_.find('.selector').removeClass('selected');
};


$(function() {
  $('[parsed_transaction_index]').each(function() {
    new pft.ParsedTransactionProcessor(
        $(this), $(this).attr('parsed_transaction_index'));
  });
});


/** Split transaction dialog */


pft.SplitTransactionDialog = function() {
  this.element_ = $('#split-transaction-dialog');

  this.categoryElements_ = [];
  this.createCategoryElement_(null, 'No category');
  for (var catId in pft.state.GetCategories()) {
    var category = pft.state.GetCategory(catId);
    this.createCategoryElement_(catId, category['name']);
  }

  var totalAmountDiv = $('<div/>').addClass('total_amount');
  totalAmountDiv.append(
      $('<span/>').addClass('first_column').text('Target total: '));
  this.totalAmount_ = $('<span/>').addClass('amount');
  totalAmountDiv.append(this.totalAmount_);
  this.element_.append(totalAmountDiv);

  this.errorDiv_ = $('<div/>').addClass('error');
  this.element_.append(this.errorDiv_);

  var me = this;
  this.element_.dialog({
    autoOpen: false,
    resizable: false,
    title: 'Split expense',
    buttons: {
      'Ok': function() {
        me.reportTransactionSplit_();
      },
      'Cancel': function() {
        $(this).dialog('close');
      }
    }
  });

  this.amount_ = null;
};


pft.SplitTransactionDialog.Dialog = null;

pft.SplitTransactionDialog.Events = {
  SPLIT: 'split'
};


pft.SplitTransactionDialog.prototype.showErrorMessage_ = function(message) {
  this.errorDiv_.text(message);
};


pft.SplitTransactionDialog.prototype.createCategoryElement_ =
    function(catId, catName) {
  var categoryElement = $('<div/>').addClass('category_splitter');

  var label = $('<span/>').addClass('category first_column').append(catName);
  categoryElement.append(label);

  var amountInput = $('<input/>').addClass('amount').
      attr('category_id', catId || '').attr('placeholder', 'None');
  categoryElement.append(amountInput);

  this.element_.append(categoryElement);
  this.categoryElements_.push(categoryElement);
};


pft.SplitTransactionDialog.prototype.reportTransactionSplit_ = function() {
  var catToAmount = {};
  this.categoryElements_.forEach(function(element) {
    var input = element.find('[category_id]');
    if (input.val()){
      catToAmount[input.attr('category_id')] =
          input.val();
    }
  });

  // Parsing
  for (var catId in catToAmount) {
    var catAmount = parseFloat(catToAmount[catId]);
    if (!catAmount || catAmount < 0.0) {
      this.showErrorMessage_(
          'All the amounts must be numbers and greater than 0.');
      return;
    }
    catToAmount[catId] = catAmount;
  }

  // Checking total sum
  var totalAmount = 0;
  for (var catId in catToAmount) {
    totalAmount += catToAmount[catId];
  }
  if (Math.abs(totalAmount - this.amount_) > 0.001) {
    this.showErrorMessage_(
        'The target total amount differs from the ' +
        'sum of categories. Remaining amount: ' +
        (this.amount_ - totalAmount).toFixed(2));
    return;
  }

  amplify.publish(pft.SplitTransactionDialog.Events.SPLIT,
                  this.transactionIndex_, catToAmount);
  this.element_.dialog('close');
};


pft.SplitTransactionDialog.prototype.open = function(transactionIndex, amount) {
  this.amount_ = amount;
  this.transactionIndex_ = transactionIndex;
  this.totalAmount_.text(amount);
  this.element_.dialog('open');
};


$(function() {
  pft.SplitTransactionDialog.Dialog = new pft.SplitTransactionDialog();
});

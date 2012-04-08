

pft.ParsedTransactionProcessor = function(element, transactionIndex) {
  this.element_ = element;

  this.transactionIndex_ = transactionIndex;

  this.selectors_ = [];
  for (var cat_id in pft.state.GetCategories()) {
    var category = pft.state.GetCategory(cat_id);
    var categorySelector = $('<a/>').attr('href', 'javascript:void(0)').
        addClass('category').text(category['name']);
    categorySelector.click(this.handleCategoryClicked.bind(
        this, cat_id, categorySelector));
    this.element_.append(categorySelector);
    this.selectors_.push(categorySelector);
  }

  this.cancelButton_ = $('<a/>').attr('href', 'javascript:void()').
      addClass('cancel_button').text('Cancel');
  this.cancelButton_.click(this.handleCancelButtonClicked.bind(this));
  this.element_.append(this.cancelButton_);
};


pft.ParsedTransactionProcessor.IMPORTED_FILE_ID = null;


pft.ParsedTransactionProcessor.prototype.handleCategoryClicked =
    function(cat_id, selector) {
  this.element_.parent().addClass('processed');
  selector.addClass('selected');
  var parsedTransaction = pft.state.GetEntity(
      this.transactionIndex_, 'parsed_transactions');
  $.post('/do/resolve_parsed_transaction', {
    'imported_file_id': pft.ParsedTransactionProcessor.IMPORTED_FILE_ID,
    'transaction_index': this.transactionIndex_,
    'category_id': cat_id});
};


pft.ParsedTransactionProcessor.prototype.handleCancelButtonClicked =
    function() {
  this.element_.parent().removeClass('processed');
  this.element_.find('.category').removeClass('selected');
};


$(function() {
  $('[parsed_transaction_index]').each(function() {
    new pft.ParsedTransactionProcessor(
        $(this), $(this).attr('parsed_transaction_index'));
  });
});

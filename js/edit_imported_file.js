

pft.ParsedTransactionProcessor = function(element, transactionIndex) {
  this.element_ = element;

  this.transactionIndex_ = transactionIndex;

  this.selectors_ = [];
  this.createSelector_(null, 'No category');
  for (var cat_id in pft.state.GetCategories()) {
    var category = pft.state.GetCategory(cat_id);
    this.createSelector_(cat_id, category['name']);
  }
  this.dropTransactionSelector_ = $('<a/>').attr('href', 'javascript:void(0)').
      addClass('category drop_button').text('Drop');
  this.dropTransactionSelector_.click(this.handleCategoryClicked.bind(
      this, cat_id, this.dropTransactionSelector_, true));

  this.element_.append(this.dropTransactionSelector_);
  this.splitTransactionSelector_ = $('<a/>').attr('href', 'javascript:void(0)').
      addClass('category').text('Split');
  this.element_.append(this.splitTransactionSelector_);

  this.cancelButton_ = $('<a/>').attr('href', 'javascript:void()').
      addClass('cancel_button').text('Cancel');
  this.cancelButton_.click(this.handleCancelButtonClicked.bind(this));
  this.element_.append(this.cancelButton_);
};


pft.ParsedTransactionProcessor.prototype.createSelector_ =
    function(cat_id, cat_name) {
  var categorySelector = $('<a/>').attr('href', 'javascript:void(0)').
      addClass('category').text(cat_name);
  categorySelector.click(this.handleCategoryClicked.bind(
      this, cat_id, categorySelector, false));
  this.element_.append(categorySelector);
  this.selectors_.push(categorySelector);
};


pft.ParsedTransactionProcessor.IMPORTED_FILE_ID = null;


pft.ParsedTransactionProcessor.prototype.handleCategoryClicked =
    function(cat_id, selector, drop) {
  this.element_.parent().addClass('processed');
  selector.addClass('selected');
  var data = {
    'imported_file_id': pft.ParsedTransactionProcessor.IMPORTED_FILE_ID,
    'transaction_index': this.transactionIndex_,
    'category_id': cat_id || ''};
  if (drop) {
    data['drop'] = '1';
  }
  $.post('/do/resolve_parsed_transaction', data);
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

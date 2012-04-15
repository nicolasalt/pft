pft.categories = {};


pft.categories.DeleteCategory = function(categoryId) {
  // TODO: implement delete
  //pft.categories.SaveCategory(categoryId, true);
};


pft.categories.EditCategory = function(categoryId) {
  var category = pft.state.GetCategory(categoryId);
  var title = 'Edit category';
  if (categoryId == '') {
    category = {
      'name': '',
      'balance': ''
    };
    title = 'Add new category';
  }
  $('#edit-category-name').val(category['name']);
  $('#edit-category-balance').val(category['balance']);
  $('#edit-category-dialog').dialog({
      resizable: false,
      title: title,
      buttons: {
        'Save': function() {
          pft.categories.SaveCategory(categoryId);
        },
        'Cancel': function() {
          $(this).dialog('close');
        }
      }
  });
};


pft.categories.SaveCategory = function(categoryId, opt_delete){
  var data = {
    'name': $('#edit-category-name').val()
  };
  var balance = $('#edit-category-balance').val();
  if (balance) {
    data['balance'] = balance;
  }
  if (categoryId) {
    data['category_id'] = categoryId;
  }
  if (opt_delete) {
    data['delete'] = '1';
  }

  $.post('/do/edit_category', data).success(function() {
    window.location.reload();
  });
  $('#edit-category-dialog').dialog('close');
};


$('[category_id]').live('click', function(){
  pft.categories.EditCategory(
      $(this).attr('category_id'));
});
$('[delete_category_id]').live('click', function(){
  pft.categories.DeleteCategory(
      $(this).attr('delete_category_id'));
});

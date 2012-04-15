
pft = {};

pft.state = {};

pft.state.State = {};


pft.state.UpdateEntity = function(entity, entityType) {
  if (!pft.state.State[entityType]) {
    pft.state.State[entityType] = {};
  }
  pft.state.State[entityType][entity['id']] = entity;
};

pft.state.GetEntity = function (entityId, entityType) {
  if (pft.state.State[entityType]) {
    return pft.state.State[entityType][entityId];
  } else {
    return null;
  }
};


pft.state.UpdateTransaction = function(transaction) {
  pft.state.UpdateEntity(transaction, 'transactions');
};

pft.state.GetTransaction = function(transactionId) {
  return pft.state.GetEntity(transactionId, 'transactions');
};


pft.state.UpdateCategory = function(category) {
  pft.state.UpdateEntity(category, 'categories');
};

pft.state.GetCategory = function(categoryId) {
  return pft.state.GetEntity(categoryId, 'categories');
};

pft.state.GetCategories = function() {
  return pft.state.State['categories'];
};

// For ordered lists. First item is 'No category'.
pft.state.GetCategoriesArray = function() {
  var result = [];
  result.push(pft.state.GetCategory(''));
  for (var catId in pft.state.GetCategories()) {
    if (catId) {
      result.push(pft.state.GetCategory(catId));
    }
  }
  return result;
};


pft.state.UpdateImportedTransaction = function(importedTransaction) {
  pft.state.UpdateEntity(importedTransaction, 'imported_transactions');
};

pft.state.GetImportedTransaction = function(transactionId) {
  return pft.state.GetEntity(transactionId, 'imported_transactions');
};


$(function() {
  // Adding empty category.
  pft.state.UpdateCategory({
    'id': '',
    'name': 'No category'});
});


pft.state.UpdateBudgetItem = function(item) {
  pft.state.UpdateEntity(item, 'budget_items');
};

pft.state.GetBudgetItem = function(itemId) {
  return pft.state.GetEntity(itemId, 'budget_items');
};


pft.state.UpdateAccount = function(account) {
  pft.state.UpdateEntity(account, 'accounts');
};

pft.state.GetAccount = function(accountId) {
  return pft.state.GetEntity(accountId, 'accounts');
};

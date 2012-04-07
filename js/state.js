
pft = {};

pft.state = {};

pft.state.State = {};


pft.state.UpdateEntity = function(entity, entity_name) {
  if (!pft.state.State[entity_name]) {
    pft.state.State[entity_name] = {};
  }
  pft.state.State[entity_name][entity['id']] = entity;
};

pft.state.GetEntity = function (entity_id, entity_name) {
  if (pft.state.State[entity_name]) {
    return pft.state.State[entity_name][entity_id];
  } else {
    return null;
  }
};

pft.state.UpdateTransaction = function(transaction) {
  pft.state.UpdateEntity(transaction, 'transactions');
};

pft.state.GetTransaction = function(transaction_id) {
  return pft.state.GetEntity(transaction_id, 'transactions');
};


pft.state.UpdateCategory = function(category) {
  pft.state.UpdateEntity(category, 'categories');
};

pft.state.GetCategory = function(category_id) {
  return pft.state.GetEntity(category_id, 'categories');
};

pft.state.GetCategories = function() {
  return pft.state.State['categories'];
};

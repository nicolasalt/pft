
pf = {};

pf.state = {};

pf.state.State = {};

pf.state.UpdateTransaction = function(transaction) {
  if (!pf.state.State['transactions']) {
    pf.state.State['transactions'] = {};
  }
  pf.state.State['transactions'][transaction['id']] = transaction;
};

pf.state.GetTransaction = function(transaction_id) {
  if (pf.state.State['transactions']) {
    return pf.state.State['transactions'][transaction_id];
  } else {
    return null;
  }
};

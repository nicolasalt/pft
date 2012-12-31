import webapp2

from handlers import import_from_file_handlers, taskqueue_handlers
from handlers import transaction_handlers
from handlers import profile_handlers
from handlers import planning_handlers
from handlers import api
from handlers import api_do


app = webapp2.WSGIApplication(
  [
    ('/api/profile/all', api.GetProfiles),
    ('/api/profile/active', api.GetActiveProfile),
    ('/api/transaction/query', api.GetTransactions),
    ('/api/do/profile/(add|edit|delete)', api_do.DoEditProfile),
    ('/api/do/profile/connect', api_do.DoConnectToProfile),
    ('/api/do/profile/set_active', api_do.DoSetActiveProfile),
    ('/api/do/account/(add|edit|delete)', api_do.DoEditAccount),
    ('/api/do/category/(add|edit|delete)', api_do.DoEditCategory),

    ('/api/get_imported_file_descriptions', api.GetImportedFileDescriptions),
    ('/api/get_imported_file', api.GetImportedFile),

    ('/api/do/add_parse_schema', api_do.DoAddParseSchema),
    ('/api/do/apply_parse_schema_to_import_file', api_do.DoApplyParseSchemaToImportedFile),

    ('/do/edit_transaction', transaction_handlers.DoEditTransaction),

    ('/edit_budget', planning_handlers.EditBudgetPage), # D
    ('/do/edit_budget_category', planning_handlers.DoEditBudgetCategory),

    ('/import_from_file', import_from_file_handlers.ImportFromFilePage),
    ('/edit_imported_file',
     import_from_file_handlers.EditImportedFilePage),
    ('/do/add_parse_schema', import_from_file_handlers.DoAddParseSchema),
    # D
    ('/do/apply_parse_schema_to_import_file',
     import_from_file_handlers.DoApplyParseSchemaToImportedFile), # D
    ('/do/resolve_parsed_transaction',
     import_from_file_handlers.DoResolveParsedTransaction),
    ('/do/add_transactions_from_csv',
     import_from_file_handlers.DoAddTransactionsFromCsv),

    ('/do/edit_user_profile_settings', profile_handlers.DoEditUserProfileSettings),

    # Taskqueues
    ('/task/update_currency_rates', taskqueue_handlers.UpdateCurrencyRates)],

  debug=True)

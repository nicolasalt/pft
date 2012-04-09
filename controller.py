import webapp2

import action_handlers
import view_handlers


app = webapp2.WSGIApplication([
    ('/', view_handlers.MainPage),
    ('/edit_budget', view_handlers.EditBudgetPage),
    ('/import_from_file', view_handlers.ImportFromFilePage),
    ('/edit_imported_file', view_handlers.EditImportedFilePage),
    ('/edit_profile', view_handlers.EditProfile),
    ('/manage_profiles', view_handlers.ManageProfilesPage),
    ('/detailed_expenses', view_handlers.DetailedExpensesPage),
    ('/do/add_profile', action_handlers.DoAddProfile),
    ('/do/add_parse_schema', action_handlers.DoAddParseSchema),
    ('/do/apply_parse_schema_to_import_file', action_handlers.DoApplyParseSchemaToImportedFile),
    ('/do/connect_to_profile', action_handlers.DoConnectToProfile),
    ('/do/set_active_profile', action_handlers.DoSetActiveProfile),
    ('/do/resolve_parsed_transaction', action_handlers.DoResolveParsedTransaction),
    ('/do/add_account', action_handlers.DoAddAccount),
    ('/do/add_category', action_handlers.DoAddCategory),
    ('/do/add_transaction', action_handlers.DoAddTransaction),
    ('/do/add_transactions_from_csv', action_handlers.DoAddTransactionsFromCsv),
    ('/do/edit_budget', action_handlers.DoEditBudget),
    ('/do/edit_profile', action_handlers.DoEditProfile)],
    debug=True)

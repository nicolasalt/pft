import webapp2

import action_handlers
from handlers import import_from_file
import view_handlers


app = webapp2.WSGIApplication([
    ('/', view_handlers.MainPage),
    ('/admin', view_handlers.AdminPage),
    ('/edit_budget', view_handlers.EditBudgetPage),
    ('/import_from_file', import_from_file.ImportFromFilePage),
    ('/edit_imported_file', import_from_file.EditImportedFilePage),
    ('/edit_profile', view_handlers.EditProfile),
    ('/manage_profiles', view_handlers.ManageProfilesPage),
    ('/detailed_expenses', view_handlers.DetailedExpensesPage),
    ('/do/add_profile', action_handlers.DoAddProfile),
    ('/do/add_parse_schema', import_from_file.DoAddParseSchema),
    ('/do/apply_parse_schema_to_import_file', import_from_file.DoApplyParseSchemaToImportedFile),
    ('/do/connect_to_profile', action_handlers.DoConnectToProfile),
    ('/do/set_active_profile', action_handlers.DoSetActiveProfile),
    ('/do/resolve_parsed_transaction', import_from_file.DoResolveParsedTransaction),
    ('/do/add_account', action_handlers.DoAddAccount),
    ('/do/add_category', action_handlers.DoAddCategory),
    ('/do/edit_transaction', action_handlers.DoEditTransaction),
    ('/do/add_transactions_from_csv', import_from_file.DoAddTransactionsFromCsv),
    ('/do/edit_profile', action_handlers.DoEditProfile)],
    debug=True)

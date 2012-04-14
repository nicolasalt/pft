import webapp2

import action_handlers
from handlers import import_from_file
from handlers import profile
from handlers import planning
import view_handlers


app = webapp2.WSGIApplication([
    ('/', view_handlers.MainPage),
    ('/admin', view_handlers.AdminPage),
    ('/transaction_report', view_handlers.TransactionReportPage),

    ('/do/add_account', action_handlers.DoAddAccount),
    ('/do/add_category', action_handlers.DoAddCategory),
    ('/do/edit_transaction', action_handlers.DoEditTransaction),

    ('/edit_budget', planning.EditBudgetPage),
    ('/do/edit_budget_category', planning.DoEditBudgetCategory),

    ('/import_from_file', import_from_file.ImportFromFilePage),
    ('/edit_imported_file', import_from_file.EditImportedFilePage),
    ('/do/add_parse_schema', import_from_file.DoAddParseSchema),
    ('/do/apply_parse_schema_to_import_file', import_from_file.DoApplyParseSchemaToImportedFile),
    ('/do/resolve_parsed_transaction', import_from_file.DoResolveParsedTransaction),
    ('/do/add_transactions_from_csv', import_from_file.DoAddTransactionsFromCsv),

    ('/edit_profile', profile.EditProfile),
    ('/manage_profiles', profile.ManageProfilesPage),
    ('/do/add_profile', profile.DoAddProfile),
    ('/do/connect_to_profile', profile.DoConnectToProfile),
    ('/do/set_active_profile', profile.DoSetActiveProfile),
    ('/do/edit_profile', profile.DoEditProfile)],
    debug=True)

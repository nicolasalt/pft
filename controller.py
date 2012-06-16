import webapp2

from handlers import import_from_file_handlers, transaction_handlers, taskqueue_handlers, other_handlers
from handlers import profile_handlers
from handlers import planning_handlers
from handlers import api


app = webapp2.WSGIApplication([
    ('/api/get_profile', api.GetProfile),

    ('/', other_handlers.MainPage),
    ('/admin', other_handlers.AdminPage),

    ('/do/edit_transaction', transaction_handlers.DoEditTransaction),
    ('/transaction_report', transaction_handlers.TransactionReportPage),

    ('/edit_budget', planning_handlers.EditBudgetPage),
    ('/do/edit_budget_category', planning_handlers.DoEditBudgetCategory),

    ('/import_from_file', import_from_file_handlers.ImportFromFilePage),
    ('/edit_imported_file', import_from_file_handlers.EditImportedFilePage),
    ('/do/add_parse_schema', import_from_file_handlers.DoAddParseSchema),
    ('/do/apply_parse_schema_to_import_file', import_from_file_handlers.DoApplyParseSchemaToImportedFile),
    ('/do/resolve_parsed_transaction', import_from_file_handlers.DoResolveParsedTransaction),
    ('/do/add_transactions_from_csv', import_from_file_handlers.DoAddTransactionsFromCsv),

    ('/settings', profile_handlers.EditProfile),
    ('/manage_profiles', profile_handlers.ManageProfilesPage),
    ('/do/edit_account', profile_handlers.DoEditAccount),
    ('/do/edit_category', profile_handlers.DoEditCategory),
    ('/do/edit_user_profile_settings', profile_handlers.DoEditUserProfileSettings),
    ('/do/add_profile', profile_handlers.DoAddProfile),
    ('/do/connect_to_profile', profile_handlers.DoConnectToProfile),
    ('/do/set_active_profile', profile_handlers.DoSetActiveProfile),
    ('/do/edit_profile', profile_handlers.DoEditProfile),

    # Taskqueues
    ('/task/update_currency_rates', taskqueue_handlers.UpdateCurrencyRates)],

    debug=True)

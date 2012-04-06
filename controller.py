import webapp2

import action_handlers
import view_handlers


app = webapp2.WSGIApplication([
    ('/', view_handlers.MainPage),
    ('/edit_budget', view_handlers.EditBudgetPage),
    ('/user_settings', view_handlers.EditProfile),
    ('/manage_profiles', view_handlers.ManageProfilesPage),
    ('/do/add_profile', action_handlers.DoAddProfile),
    ('/do/connect_to_profile', action_handlers.DoConnectToProfile),
    ('/do/set_active_profile', action_handlers.DoSetActiveProfile),
    ('/do/add_account', action_handlers.DoAddAccount),
    ('/do/add_category', action_handlers.DoAddCategory),
    ('/do/add_transaction', action_handlers.DoAddTransaction),
    ('/do/add_transactions_from_csv', action_handlers.DoAddTransactionsFromCsv),
    ('/do/edit_budget', action_handlers.DoEditBudget),
    ('/do/edit_profile', action_handlers.DoEditProfile)],
    debug=True)

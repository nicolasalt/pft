import webapp2

import action_handlers
import view_handlers


app = webapp2.WSGIApplication([
    ('/', view_handlers.MainPage),
    ('/edit_budget', view_handlers.EditBudgetPage),
    ('/user_settings', view_handlers.UserSettingsPage),
    ('/create_user', view_handlers.CreateUserPage),
    ('/do/create_user', action_handlers.DoCreateUser),
    ('/do/add_account', action_handlers.DoAddAccount),
    ('/do/add_category', action_handlers.DoAddCategory),
    ('/do/add_transaction', action_handlers.DoAddTransaction),
    ('/do/edit_budget', action_handlers.DoEditBudget),
    ('/do/edit_user_settings', action_handlers.DoEditUserSettings)],
    debug=True)

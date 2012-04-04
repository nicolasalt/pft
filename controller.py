import webapp2

import action_handlers
import view_handlers


app = webapp2.WSGIApplication([
    ('/', view_handlers.MainPage),
    ('/edit_budget', view_handlers.EditBudgetPage),
    ('/do/add_account', action_handlers.DoAddAccount),
    ('/do/add_category', action_handlers.DoAddCategory),
    ('/do/add_transaction', action_handlers.DoAddTransaction),
    ('/do/edit_budget', action_handlers.DoEditBudget),
    ('/do/edit_user_settings', action_handlers.DoEditUserSettings)],
    debug=True)

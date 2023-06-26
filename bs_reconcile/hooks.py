from . import __version__ as app_version

app_name = "bs_reconcile"
app_title = "Balance Sheet Reconciliation"
app_publisher = "FLO WORKS"
app_description = "Allow reconcile all balance sheet gl entry"
app_email = "kittiu@flo-works.co"
app_license = "MIT"
required_apps = ["erpnext"]

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			[
				"name",
				"in",
				(
					"Account-is_reconcile",
					"GL Entry-full_reconcile_number",
					"GL Entry-residual",
					"GL Entry-is_reconcile",
					"GL Entry-section_break_qneej",
				),
			]
		],
	}
]


# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/bs_reconcile/css/bs_reconcile.css"
# app_include_js = "/assets/bs_reconcile/js/bs_reconcile.js"

# include js, css files in header of web template
# web_include_css = "/assets/bs_reconcile/css/bs_reconcile.css"
# web_include_js = "/assets/bs_reconcile/js/bs_reconcile.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "bs_reconcile/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# monkey patch
import erpnext.accounts.general_ledger

import bs_reconcile.overrides.general_ledger

erpnext.accounts.general_ledger.set_as_cancel = (
	bs_reconcile.overrides.general_ledger.set_as_cancel
)

# include js in doctype views
doctype_js = {"GL Entry": "public/js/gl_entry.js"}
doctype_list_js = {"GL Entry": "public/js/gl_entry_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "bs_reconcile.utils.jinja_methods",
# 	"filters": "bs_reconcile.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "bs_reconcile.install.before_install"
# after_install = "bs_reconcile.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "bs_reconcile.uninstall.before_uninstall"
# after_uninstall = "bs_reconcile.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "bs_reconcile.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Payment Reconciliation": "bs_reconcile.overrides.payment_reconciliation.BSPaymentReconciliation",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"GL Entry": {
		"after_insert": "bs_reconcile.overrides.gl_entry.bs_reconcile",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"bs_reconcile.tasks.all"
# 	],
# 	"daily": [
# 		"bs_reconcile.tasks.daily"
# 	],
# 	"hourly": [
# 		"bs_reconcile.tasks.hourly"
# 	],
# 	"weekly": [
# 		"bs_reconcile.tasks.weekly"
# 	],
# 	"monthly": [
# 		"bs_reconcile.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "bs_reconcile.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "bs_reconcile.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "bs_reconcile.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["bs_reconcile.utils.before_request"]
# after_request = ["bs_reconcile.utils.after_request"]

# Job Events
# ----------
# before_job = ["bs_reconcile.utils.before_job"]
# after_job = ["bs_reconcile.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"bs_reconcile.auth.validate"
# ]

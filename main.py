
import sys
from PySide2.QtWidgets import QApplication, QDialog

import authorize as login
import browser as brws
import noadmin_browser as no_brws


def main():
	
	app = QApplication(sys.argv)
	login_form = login.AuthorizeWindow()
	
	login_state = login_form.exec_()
	
	if login_state == QDialog.Accepted:
		if login_form.login.text() == "user":
			win = no_brws.Window()
			win.show()
		elif login_form.login.text() == "admin":
			win = brws.Window()
			win.show()
	elif login_state == QDialog.Rejected:
		sys.exit(app.exec_())
	
	sys.exit(app.exec_())
	
if __name__ == '__main__':
	main()

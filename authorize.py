from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (QGridLayout, QPushButton, \
                               QLineEdit, QDialog, QLabel)

import sqlconnect as sql


class AuthorizeWindow(QDialog):
	
	PATH_TO_DB = "database_storage/personal.db"
	SQL_CON = sql.Connect(PATH_TO_DB)
	
	def __init__(self):
		super().__init__()
		self.enter, self.layout, self.password, self.login = None, None, None, None
		self.init_gui()
	
	# Иницилизируем GUI
	def init_gui(self):
		self.resize(300, 50)
		self.setWindowTitle("Авторизация")
		self.setWindowIcon(QIcon("app_icon.png"))
		
		layout = QGridLayout()
		
		# Создание элементов интерфейса окна
		self.login = QLineEdit()
		self.password = QLineEdit()
		self.enter = QPushButton("Принять")
		self.enter.clicked.connect(self.enter_accept)
		
		for widget in (QLabel("Введите логин:"), self.login, QLabel("Введите пароль:"), self.password, self.enter):
			layout.addWidget(widget)
		self.setLayout(layout)
	
	# Функция для входа (Login form)
	def enter_accept(self):
		output = AuthorizeWindow.SQL_CON.query(f"select id from Users where login = "
		                   f"'{self.login.text()}' and pswd = '{self.password.text()}'")
		if bool(output):
			self.accept()

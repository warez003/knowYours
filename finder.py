from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QGridLayout, \
	QLineEdit, QPushButton, QLabel

import sqlconnect as sql

class Find(QDialog):
	
	PATH = "database_storage/personal.db"
	TOOL = sql.Connect(PATH)
	
	def __init__(self):
		super().__init__()
		self.find_value = None
		self.find_button = None
		self.initg()
	
	def initg(self):
		self.setWindowTitle("Поиск")
		self.resize(300, 50)
		self.setWindowIcon(QIcon("app_icon.png"))
		
		layout = QGridLayout()
		
		self.find_value = QLineEdit()
		self.find_button = QPushButton("Поиск")
		self.find_button.clicked.connect(self.find_event)
		
		for widget in [QLabel("Введите ФИО студента для поиска: "), self.find_value, self.find_button]:
			layout.addWidget(widget)
		self.setLayout(layout)
	
	def find_event(self):
		if Find.TOOL.query(f"select * from Students where name = '{self.find_value.text()}'"):
			self.accept()
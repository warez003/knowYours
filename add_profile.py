from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QGridLayout, \
	QLineEdit, QPushButton, QLabel

class Add(QDialog):
	
	def __init__(self):
		super().__init__()
		self.student_group = None
		self.add_button = None
		self.student_name = None
		self.initg()
	
	def initg(self):
		self.setWindowTitle("Добавить запись студента")
		self.resize(300, 50)
		self.setWindowIcon(QIcon("app_icon.png"))
		
		layout = QGridLayout()
		
		self.student_name = QLineEdit()
		self.student_group = QLineEdit()
		self.add_button = QPushButton("Добавить запись")
		self.add_button.clicked.connect(self.add_event)
		
		widgets = (QLabel("Введите ФИО студента"), self.student_name, QLabel("Введите название группы студента"),
		           self.student_group, self.add_button)
		for widget in widgets:
			layout.addWidget(widget)
		self.setLayout(layout)
	
	def add_event(self):
		if len(self.student_name.text()) > 0 and len(self.student_group.text()) > 0:
			self.accept()
			
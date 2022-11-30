import os.path
import shutil

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QGridLayout, \
	QLineEdit, QPushButton, QLabel

import sqlconnect as sql


class Delete(QDialog):
	
	DB_PATH = "database_storage/personal.db"
	SQLITE_CON = sql.Connect(DB_PATH)
	
	def __init__(self):
		super().__init__()
		self.delete_button = None
		self.student_name = None
		self.initg()
	
	def initg(self):
		self.setWindowTitle("Стереть запись студента")
		self.resize(300, 50)
		self.setWindowIcon(QIcon("app_icon.png"))
		
		layout = QGridLayout()
		
		self.student_name = QLineEdit()
		self.delete_button = QPushButton("Стереть запись")
		self.delete_button.clicked.connect(self.delete_event)
		
		for widget in [QLabel("Введите ФИО студента, чтобы удалить запись"), self.student_name, self.delete_button]:
			layout.addWidget(widget)
		self.setLayout(layout)
	
	def delete_event(self):
		Delete.SQLITE_CON.query(f"delete from Students where name = '{self.student_name.text()}'")
		
		storage_path = Delete.SQLITE_CON.query(f"select path from Storage where name = '{self.student_name.text()}'")
		for elements in storage_path:
			storage_path = elements[0]
		if bool(storage_path):
			shutil.rmtree(os.path.relpath(storage_path))
		
		group_for_delete = Delete.SQLITE_CON.query(f"select student_group from Students where name = "
		                                       f"'{self.student_name.text()}'")
		for elements in group_for_delete:
			group_for_delete = elements[0]
		count_student_for_delete_group = Delete.SQLITE_CON.query(f"select count(id) from Students "
		                                                     f"where student_group = '{group_for_delete}'")
		for elements in count_student_for_delete_group:
			count_student_for_delete_group = elements[0]
		if int(count_student_for_delete_group) <= 1:
			Delete.SQLITE_CON.query(f"delete from Groups where name = '{group_for_delete}'")
			
		Delete.SQLITE_CON.query(f"delete from Storage where name = '{self.student_name.text()}'")
		Delete.SQLITE_CON.query(f"delete from Pictures where name = '{self.student_name.text()}'")
		Delete.SQLITE_CON.query(f"delete from Docs where name = '{self.student_name.text()}'")
		
		self.accept()

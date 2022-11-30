from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QDialog, QGridLayout, \
	QLabel

class About(QDialog):
	
	def __init__(self):
		super().__init__()
		self.initg()
	
	def initg(self):
		self.setWindowTitle("Информация о приложении и авторе")
		self.resize(300, 50)
		self.setWindowIcon(QIcon("app_icon.png"))
		
		layout = QGridLayout()
		
		lb1 = QLabel()
		lb1.setPixmap(QPixmap("app_icon.png"))
		lb1.resize(150, 100)
		
		lb2 = QLabel("<b>Знай своих!<b>")
		lb3 = QLabel("v0.1")
		lb4 = QLabel("Знай своих! - это простая программа для просмотра и создания профилей\n "
		             "студентов и их личных данных.")
		lb5 = QLabel("Copyright © 2022 - the Independent developers")
		lb6 = QLabel("Это приложение распространяется без каких-либо гарантий.\n Подробнее в GNU Lesser "
		             "General Public License, версии 2 или позднее")
		
		for widget in [lb1, lb2, lb3, lb4, lb5, lb6]:
			widget.setAlignment(Qt.AlignCenter)
			layout.addWidget(widget)
		
		self.setLayout(layout)

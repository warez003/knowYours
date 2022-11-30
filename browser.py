
import os
import random
import subprocess
from pathlib import Path

from PIL import Image
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import (QWidget, QMainWindow, QListWidget, QLabel, QGridLayout, \
                               QComboBox, QDesktopWidget, QDialog)

import about as app_info
import add_profile as adder
import delete_profile as delete_form
import finder as fnd
import sqlconnect as sql


class Window(QMainWindow):
    # Отдел констант
    SQLITE_DB_PATH = "database_storage/personal.db"
    DATABASE = sql.Connect(SQLITE_DB_PATH)
    STUDENT_IMG_SIZE = (424, 240)
    
    def __init__(self):
        super().__init__()
        self.student_img = None
        self.refresh = None
        self.last_selected = None
        self.groups, self.profiles, self.profile_pic, self.main_widget, \
        self.docs, self.info = None, None, None, None, None, None
        self.delete_record = None
        self.last_index_CB = None
        self.init_ui()
        self.init_data()
    
    # Функция для иницилизации GUI
    def init_ui(self):
        
        self.resize(1024, 768)
        self.setWindowTitle("Знай своих!")
        self.setWindowIcon(QIcon("app_icon.png"))

        layout = QGridLayout()
        
        self.main_widget = QWidget()
        bar = self.menuBar()
        file = bar.addMenu("Файл")
        data_actions = bar.addMenu("Данные")
        new_record = file.addAction("Новая запись")
        about_prog = bar.addMenu("Справка")
        about_app = about_prog.addAction("О программе")
        about_app.triggered.connect(self.get_info)
        self.refresh = data_actions.addAction("Обновить")
        find = data_actions.addAction("Поиск")
        find.triggered.connect(self.find_in_db)
        self.refresh.triggered.connect(self.refresh_data)
        self.delete_record = file.addAction("Удалить запись")
        self.delete_record.triggered.connect(self.dlt)
        new_record.triggered.connect(self.add_record)
        self.docs = QListWidget()
        self.docs.itemClicked.connect(self.docs_view)
        self.info = QListWidget()
        self.groups = QComboBox()
        self.groups.currentIndexChanged.connect(self.load)
        self.profiles = QListWidget()
        
        self.profiles.itemClicked.connect(self.profile_view)
        self.profile_pic = QLabel()
        img = Image.open('null_image.jpg')
        img = img.resize((640, 480))
        img.save('null_image.jpg')
        student_pic = QPixmap('null_image.jpg')
        self.profile_pic.setPixmap(QPixmap(student_pic))
        
        layout.addWidget(self.profile_pic, 1, 1, 1, 1)
        layout.addWidget(self.info, 1, 2, 1, 1)
        layout.addWidget(self.docs, 2, 1, 2, 2)
        layout.addWidget(self.groups, 0, 3, 1, 1)
        layout.addWidget(self.profiles, 1, 3, 3, 1)
        
        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)
        self.center_to_screen()
    
    @staticmethod
    def get_info():
        about_form = app_info.About()
        about_form.exec_()
    
    def find_in_db(self):
        finder_form = fnd.Find()
        if finder_form.exec_() == QDialog.Accepted:
            need_student = finder_form.find_value.text()
            self.profiles.setCurrentItem(self.profiles.findItems(need_student, Qt.MatchExactly)[0])
            self.profile_view(self.profiles.currentItem())
    
    def refresh_data(self):
        self.groups.clear()
        self.docs.clear()
        self.info.clear()
        
        if bool(self.last_selected):
            # Получаем информацию о группах студентов и заполняем ими listBox
            groups_with_no_students = Window.DATABASE.query(f"select name from Groups where name not in "
                                                            f"(select student_group from Students)")
            for elements in groups_with_no_students:
                for element in elements:
                    Window.DATABASE.query(f"delete from Groups where name = '{element}'")

            students_with_undef_group = Window.DATABASE.query(f"select name from Students where student_group not in "
                                                              f"(select name from Groups)")
            for elements in students_with_undef_group:
                for element in elements:
                    Window.DATABASE.query(f"delete from Students where name = '{element}'")
            
            self.init_data()
            self.load()
    
            # Получаем информацию о конкретном студенте
            c = 0
            current_student_info = Window.DATABASE.query(
                f"select name, student_group from Students where name = '{self.last_selected}'")
            if current_student_info is not None:
                for elements in current_student_info:
                    while c < len(elements):
                        if c == 0:
                            self.info.addItem("ФИО студента: " + elements[c])
                        elif c == 1:
                            self.info.addItem("Группа студента: " + elements[c])
                        c += 1
                docs_count = Window.DATABASE.query(f"select files_count from Docs where storage_id = "
                                                   f"(select id from Storage where name = '{self.last_selected}')")
                for elements in docs_count:
                    docs_count = elements[0]
                if bool(docs_count):
                    self.info.addItem("Кол-во загруженных документов: " + str(docs_count))
    
                # Создаём приватную директорию для конкретного студента
                # В ней будут хранится фотографии для профиля и документы личных дел
                user_storage_path = Window.DATABASE.query(f"select path from Storage "
                                                          f"where name = '{self.last_selected}'")
                if not bool(user_storage_path):
                    student_name = Window.DATABASE.query(f"select name from Students "
                                                         f"where name = '{self.last_selected}'")
                    for elements in student_name:
                        student_name = elements[0]
                    if bool(student_name):
                        new_path = os.path.join(os.path.abspath(os.getcwd()), student_name)
                        Window.DATABASE.query(f"insert into Storage(name, path, id) "
                                              f"values ('{self.last_selected}', "
                                              f"'{new_path}', '{random.randint(1, 1231244)}')")
                        user_storage_path = new_path
                else:
                    for elements in user_storage_path:
                        user_storage_path = elements[0]
    
                # Создаём директории для storage/ и user_storage_path/ если их не существует
                if bool(user_storage_path):
                    if not os.path.exists(user_storage_path):
                        os.makedirs(user_storage_path)
    
                # Получаем путь к папке с документами из БД
                # Если нет, то создаем директорию для документов
                path_to_docs = Window.DATABASE.query(f"select path from Docs where storage_id = "
                                                     f"(select id from Storage "
                                                     f"where name = '{self.last_selected}')")
                if not bool(path_to_docs):
                    docs_path = os.path.join(user_storage_path, 'docs')
                    Window.DATABASE.query(f"insert into Docs(name, path, storage_id) values "
                                          f"('{self.last_selected}', '{docs_path}', "
                                          f"(select id from Storage where name = "
                                          f"'{self.last_selected}'))")
                    path_to_docs = docs_path
                else:
                    for elements in path_to_docs:
                        path_to_docs = elements[0]
    
                # Получаем путь к папке с фотографиями из БД
                # Если нет, то создаем директорию для фотографий профиля
                path_to_pictures = Window.DATABASE.query(f"select path from Pictures where storage_id = "
                                                         f"(select id from Storage "
                                                         f"where name = '{self.last_selected}')")
                if not bool(path_to_pictures):
                    pictures = os.path.join(user_storage_path, 'pictures')
                    Window.DATABASE.query(f"insert into Pictures(name, path, storage_id) "
                                          f"values ('{self.last_selected}', "
                                          f"'{pictures}', (select id from Storage "
                                          f"where name = '{self.last_selected}'))")
                    path_to_pictures = pictures
                else:
                    for elements in path_to_pictures:
                        path_to_pictures = elements[0]
    
                if bool(path_to_pictures):
                    if not os.path.exists(path_to_docs):
                        os.makedirs(path_to_docs)
                    if not os.path.exists(path_to_pictures):
                        os.makedirs(path_to_pictures)
    
                # Обновляем данные в таблицу Docs и заполняем listBox названиями файлов (документов)
                update_path = Window.DATABASE.query(f"select path from Docs where storage_id = "
                                                    f"(select id from Storage "
                                                    f"where name = '{self.last_selected}')")
                for elements in update_path:
                    update_path = elements[0]
                if bool(update_path):
                    files_count = 0
                    for element in os.listdir(update_path):
                        pfile = Path(f'{update_path}/{element}')
                        if pfile.is_file():
                            self.docs.addItem(element)
                            files_count += 1
                    Window.DATABASE.query(f"update Docs set files_count = {files_count} "
                                          f"where storage_id = (select id from Storage "
                                          f"where name = '{self.last_selected}')")
    
                # Загружаем картинку профиля из пути в таблице Pictures, что в БД
                path_to_pic_storage = Window.DATABASE.query(f"select path from Pictures where storage_id = "
                                                            f"(select id from Storage "
                                                            f"where name = '{self.last_selected}')")
                for elements in path_to_pic_storage:
                    path_to_pic_storage = elements[0]
                if bool(path_to_pic_storage):
                    if os.path.exists(f"{path_to_pic_storage}/default.jpg"):
                        self.student_img = f"{path_to_pic_storage}/default.jpg"
                        preview = Image.open(f"{path_to_pic_storage}/default.jpg")
                        preview = preview.resize(Window.STUDENT_IMG_SIZE)
                        preview.save(f"{path_to_pic_storage}/default.jpg")
                        self.profile_pic.setPixmap(QPixmap(self.student_img))
                    elif not os.path.exists(self.student_img):
                        self.profile_pic.setPixmap(QPixmap("null_image.jpg"))
                    
        elif not bool(self.last_selected):
    
            students_with_undef_group = Window.DATABASE.query(f"select name from Students where student_group not in "
                                                              f"(select name from Groups)")
            for elements in students_with_undef_group:
                for element in elements:
                    Window.DATABASE.query(f"delete from Students where name = '{element}'")

            groups_with_no_students = Window.DATABASE.query(f"select name from Groups where name not in "
                                                            f"(select student_group from Students)")
            for elements in groups_with_no_students:
                for element in elements:
                    Window.DATABASE.query(f"delete from Groups where name = '{element}'")
            
            self.init_data()
            self.load()
            
    
    def dlt(self):
        form = delete_form.Delete()
        if form.exec_() == QDialog.Accepted:
            self.refresh_data()
    
    def docs_view(self):
        path_to_current_doc = Window.DATABASE.query(f"select path from Docs where storage_id = "
                              f"(select id from Storage where name = '{self.profiles.selectedItems()[0].text()}')")
        for elements in path_to_current_doc:
            path_to_current_doc = elements[0]
        if bool(path_to_current_doc):
            path_to_current_doc += f"/{self.docs.selectedItems()[0].text()}"
            subprocess.call(["exo-open", path_to_current_doc])
    
    def add_record(self):
        add_form = adder.Add()
        if add_form.exec_() == QDialog.Accepted:
            group_exist = Window.DATABASE.query(f"select * from Groups where name = "
                                                f"'{add_form.student_group.text()}'")
            for elements in group_exist:
                group_exist = elements[0]
            if not bool(group_exist):
                student_exist = Window.DATABASE.query(f"select * from "
                                                      f"Students where name = '{add_form.student_name.text()}'")
                for elements in student_exist:
                    student_exist = elements[0]
                if not bool(student_exist):
                    Window.DATABASE.query(f"insert into Groups (id, name) values "
                                          f"('{random.randint(1, 1231244)}', '{add_form.student_group.text()}')")
                    Window.DATABASE.query(f"insert into Students (name, student_group, groups_id) "
                                          f"values ('{add_form.student_name.text()}', "
                                          f"'{add_form.student_group.text()}', "
                                          f"(select id from Groups where name = '{add_form.student_group.text()}'))")
                    self.groups.addItem(add_form.student_group.text())
            elif bool(group_exist):
                student_exist = Window.DATABASE.query(f"select * from "
                                                      f"Students where name = '{add_form.student_name.text()}'")
                for elements in student_exist:
                    student_exist = elements[0]
                if not bool(student_exist):
                    Window.DATABASE.query(f"insert into Students (name, student_group, groups_id) "
                                          f"values ('{add_form.student_name.text()}', "
                                          f"'{add_form.student_group.text()}', "
                                          f"(select id from Groups where name = '{add_form.student_group.text()}'))")
            grp = Window.DATABASE.query(f"select student_group from Students "
                                  f"where name = '{add_form.student_name.text()}'")
            for elements in grp:
                grp = elements[0]
            if self.groups.currentText() == grp:
                self.profiles.addItem(add_form.student_name.text())
            self.last_index_CB = self.groups.currentIndex()
            self.refresh_data()
    
    def init_data(self):
        self.groups.clear()
        
        # Получаем информацию о группах студентов и заполняем ими listBox
        groups = Window.DATABASE.query("select name from Groups")
        if bool(groups):
            for group in groups:
                self.groups.addItem(group[0])
        if bool(self.last_index_CB):
            self.groups.setCurrentIndex(self.last_index_CB)
    
    def profile_view(self, item):
        self.info.clear()
        self.docs.clear()
        self.last_selected = item.text()
        
        # Получаем информацию о конкретном студенте
        c = 0
        current_student_info = Window.DATABASE.query(
            f"select name, student_group from Students where name = '{item.text()}'")
        if bool(current_student_info):
            for elements in current_student_info:
                while c < len(elements):
                    if c == 0:
                        self.info.addItem("ФИО студента: " + elements[c])
                    elif c == 1:
                        self.info.addItem("Группа студента: " + elements[c])
                    c += 1
            docs_count = Window.DATABASE.query(f"select files_count from Docs where storage_id = "
                                               f"(select id from Storage where name = '{item.text()}')")
            for elements in docs_count:
                docs_count = elements[0]
            self.info.addItem("Кол-во загруженных документов: " + str(docs_count))
        
        # Создаём приватную директорию для конкретного студента
        # В ней будут хранится фотографии для профиля и документы личных дел
        user_storage_path = Window.DATABASE.query(f"select path from Storage where name = '{item.text()}'")
        if not bool(user_storage_path):
            student_name = Window.DATABASE.query(f"select name from Students where name = '{item.text()}'")
            for elements in student_name:
                student_name = elements[0]
            new_path = os.path.join(os.path.abspath(os.getcwd()), student_name)
            Window.DATABASE.query(f"insert into Storage(name, path, id) "
                                  f"values ('{item.text()}', '{new_path}', '{random.randint(1, 1231244)}')")
            user_storage_path = new_path
        else:
            for elements in user_storage_path:
                user_storage_path = elements[0]
        
        # Создаём директории для storage/ и user_storage_path/ если их не существует
        if bool(user_storage_path):
            if not os.path.exists(user_storage_path):
                os.makedirs(user_storage_path)
        
        # Получаем путь к папке с документами из БД
        # Если нет, то создаем директорию для документов
        path_to_docs = Window.DATABASE.query(f"select path from Docs where storage_id = "
                                             f"(select id from Storage where name = '{item.text()}')")
        if not bool(path_to_docs):
            docs_path = os.path.join(user_storage_path, 'docs')
            Window.DATABASE.query(f"insert into Docs(name, path, storage_id) values "
                                  f"('{item.text()}', '{docs_path}', "
                                  f"(select id from Storage where name = '{item.text()}'))")
            path_to_docs = docs_path
        else:
            for elements in path_to_docs:
                path_to_docs = elements[0]
        
        # Получаем путь к папке с фотографиями из БД
        # Если нет, то создаем директорию для фотографий профиля
        path_to_pictures = Window.DATABASE.query(f"select path from Pictures where storage_id = "
                                                 f"(select id from Storage where name = '{item.text()}')")
        if not bool(path_to_pictures):
            pictures = os.path.join(user_storage_path, 'pictures')
            Window.DATABASE.query(f"insert into Pictures(name, path, storage_id) "
                                  f"values ('{item.text()}', "
                                  f"'{pictures}', (select id from Storage where name = '{item.text()}'))")
            path_to_pictures = pictures
        else:
            for elements in path_to_pictures:
                path_to_pictures = elements[0]
            
        
        if bool(path_to_docs):
            if not os.path.exists(path_to_docs):
                os.makedirs(path_to_docs)
        if bool(path_to_pictures):
            if not os.path.exists(path_to_pictures):
                os.makedirs(path_to_pictures)
        
        # Обновляем данные в таблицу Docs и заполняем listBox названиями файлов (документов)
        update_path = Window.DATABASE.query(f"select path from Docs where storage_id = "
                                            f"(select id from Storage where name = '{item.text()}')")
        for elements in update_path:
            update_path = elements[0]
        files_count = 0
        for element in os.listdir(update_path):
            pfile = Path(f'{update_path}/{element}')
            if pfile.is_file():
                self.docs.addItem(element)
                files_count += 1
        Window.DATABASE.query(f"update Docs set files_count = {files_count} "
                              f"where storage_id = (select id from Storage where name = '{item.text()}')")
        
        # Загружаем картинку профиля из путя в таблице Pictures, что в БД
        path_to_pic_storage = Window.DATABASE.query(f"select path from Pictures where storage_id = "
                                                    f"(select id from Storage where name = '{item.text()}')")
        for elements in path_to_pic_storage:
            path_to_pic_storage = elements[0]
        if os.path.exists(f"{path_to_pic_storage}/default.jpg"):
            self.profile_pic.setPixmap(QPixmap(f"{path_to_pic_storage}/default.jpg"))
        elif not os.path.exists(f"{path_to_pic_storage}/default.jpg"):
            self.profile_pic.setPixmap(QPixmap("null_image.jpg"))
    
    # Функция для заполнения listBox с именами студентов
    def load(self):
        if not bool(self.groups.currentText()):
            self.groups.setCurrentIndex(0)
        self.profiles.clear()
        
        students_profiles = Window.DATABASE.query(
            f"select name from Students where student_group = '{self.groups.currentText()}'")
        if bool(students_profiles):
            for part in students_profiles:
                self.profiles.addItem(part[0])
    
    # Функция для центрирования окна приложения по середине экрана
    def center_to_screen(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QComboBox, QLabel, QFileDialog
from timetable import Timetable


class PreMain(QWidget):
    def __init__(self):
        super(PreMain, self).__init__()
        uic.loadUi('premain.ui', self)
        self.greeting.setText('Перед началом работы загрузите таблицу на:')
        self.mon_lbl.setText('Понедельник')
        self.tue_lbl.setText('Вторник')
        self.wed_lbl.setText('Среду')
        self.thur_lbl.setText('Четверг')
        self.fri_lbl.setText('Пятницу')

        self.mon_btn.setText('Выбрать на понедельник')
        self.tue_btn.setText('Выбрать на вторник')
        self.wed_btn.setText('Выбрать на среду')
        self.thur_btn.setText('Выбрать на четверг')
        self.fri_btn.setText('Выбрать на пятницу')

        self.go_btn.setText('Поехали!')

        self.buttonGroup.buttonClicked.connect(self.run)
        self.go_btn.clicked.connect(self.open_main)

    def run(self, btn):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать таблицу',
                                            '', "Таблица(*.xlsx)")[0]
        Timetable().create_shedule(fname, btn.text())
        btn.setText('Выбран файл:{}'.format(fname.split('/')[-1]))

    def open_main(self):
        Timetable().create_class_subject_teacher_table()
        self.main = Main()
        self.main.show()
        self.close()
        # переход в главное окно


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.parent_to_second_btn.clicked.connect(self.open_second_parent_form)
        self.student_to_second_btn.clicked.connect(self.open_second_student_form)

    def open_second_parent_form(self):
        self.second_parent_form = SecondParentForm()
        self.second_parent_form.show()
        self.close()
        # Открытие формы для родителя

    def open_second_student_form(self):
        self.second_student_form = SecondStudentForm()
        self.second_student_form.show()
        self.close()
        # Открытие формы для ученика


class SecondParentForm(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('secondparent.ui', self)
        self.parent_class_combo.addItems(sorted(Timetable().create_list_of_classes()))
        self.parent_sub_combo.addItems(sorted(Timetable().create_list_of_subjects()))

        self.parent_class_lbl.setText('Выберите класс')
        self.parent_sub_lbl.setText('Выберите предмет')

        self.go_btn.setText('Поехали!')
        self.back_btn.setText('Назад')

        self.back_btn.clicked.connect(self.btnBack)
        self.go_btn.clicked.connect(self.open_direction)

    def btnBack(self):
        self.main = Main()
        self.main.show()
        self.close()

    def open_direction(self):
        cl = str(self.parent_class_combo.currentText())
        sub = str(self.parent_sub_combo.currentText())
        self.direction_form = ParentDirection(self, cl, sub)
        self.direction_form.show()
        self.close()


class SecondStudentForm(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('secondstudent.ui', self)
        self.student_class_combo.addItems(sorted(Timetable().create_list_of_classes()))

        self.student_class_lbl.setText('Выберите класс')

        self.go_btn.setText('Поехали!')
        self.back_btn.setText('Назад')

        self.back_btn.clicked.connect(self.btnBack)
        self.go_btn.clicked.connect(self.open_direction)

    def btnBack(self):
        self.main = Main()
        self.main.show()
        self.close()

    def open_direction(self):
        cl = str(self.student_class_combo.currentText())
        self.direction_form = StudentDirection(self, cl)
        self.direction_form.show()
        self.close()


class ParentDirection(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('parentdirection.ui', self)
        self.cl = args[1]
        self.sub = args[2]
        room, teacher = Timetable().get_value_for_parent(self.cl, self.sub)
        self.back_btn.setText('Назад')
        self.to_main_btn.setText('Вернуться на главную')
        self.back_btn.clicked.connect(self.btnBack)
        self.to_main_btn.clicked.connect(self.btnToMain)
        self.room_lbl.setText(room)
        self.teacher_lbl.setText(teacher)

    def btnBack(self):
        self.second_parent_form = SecondParentForm()
        self.second_parent_form.show()
        self.close()

    def btnToMain(self):
        self.main = Main()
        self.main.show()
        self.close()


class StudentDirection(QWidget):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('studentdirection.ui', self)
        cl = args[1]
        room, teacher = Timetable().get_value_for_student(cl)
        self.back_btn.setText('Назад')
        self.to_main_btn.setText('Вернуться на главную')
        self.back_btn.clicked.connect(self.btnBack)
        self.to_main_btn.clicked.connect(self.btnToMain)
        self.room_lbl.setText(room)
        self.teacher_lbl.setText(teacher)

    def btnBack(self):
        self.second_parent_form = SecondParentForm()
        self.second_parent_form.show()
        self.close()

    def btnToMain(self):
        self.main = Main()
        self.main.show()
        self.close()


app = QApplication(sys.argv)
ex = PreMain()
ex.show()
sys.exit(app.exec_())

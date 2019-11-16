import xlrd
import sqlite3
from datetime import datetime, time

now = datetime.now()
megashedule = []
calls = []


class Timetable:
    def create_shedule(self, fname, btn_text):
        self.btn_text = btn_text
        self.file_name = fname
        self.table_name = ''
        wb = xlrd.open_workbook('{}'.format(self.file_name))
        sh = wb.sheet_by_name('Лист1')
        data = []
        bells = []

        for rownum in range(sh.nrows):
            data.append(list(filter(None, sh.row_values(rownum))))

        for i in range(1, 21, 3):
            bells.append(data[i][0])
        # Создание списка звонков
        calls.append(list(map(lambda x: x.split('-'), bells)))
        post_data = list(filter(None, data))
        # Считывание данных с exel таблицы и очистка от пустых значений
        shedule = []
        for k in range(len(post_data) // 7):
            for i in range(len(post_data[0])):
                for j in range(7):
                    try:
                        shedule.append([post_data[k * 22][i],
                                        int(post_data[(k * 22) + 3 * j + 1][1]),
                                        post_data[(k * 22) + 3 * j + 1][i + 2].strip(),
                                        post_data[(k * 22) + 3 * j + 2][i].strip(),
                                        post_data[(k * 22) + 3 * j + 3][i].strip()])
                    except Exception:
                        pass
        # Заполнение списка данными из exel таблицы
        for k in range(len(post_data) // 7):
            for i in range(len(post_data[0])):
                for j in range(7):
                    try:
                        megashedule.append([post_data[k * 22][i],  # 7 * 3 + 1
                                            post_data[(k * 22) + 3 * j + 1][i + 2].strip(),
                                            post_data[(k * 22) + 3 * j + 3][i].strip()])
                    except Exception:
                        pass
        # Заполнение большей таблицы, для опредления у какого класса по какому предмету
        # какой преподаватель ведет уроки

        if 'понедельник' in self.btn_text:
            self.table_name = 'mon_shedule'
        elif 'вторник' in self.btn_text:
            self.table_name = 'tue_shedule'
        elif 'среду' in self.btn_text:
            self.table_name = 'wed_shedule'
        elif 'четверг' in self.btn_text:
            self.table_name = 'thur_shedule'
        elif 'пятницу' in self.btn_text:
            self.table_name = 'fri_shedule'
        # Определение с какой кнопки был послан сигнал, и в какую таблицу SQL заносить данные
        con = sqlite3.connect('timetable.db')
        cur = con.cursor()
        cur.execute("""DELETE FROM {}""".format(self.table_name))
        for e in shedule:
            cur.execute("""INSERT INTO {} VALUES (?, ?, ?, ?, ?)""".format(self.table_name), e)
        con.commit()
        con.close()
        shedule.clear()
        # Заполнение таблицы

    def create_list_of_classes(self):
        con = sqlite3.connect('timetable.db')
        cur = con.cursor()
        pre_result = cur.execute("""SELECT DISTINCT class FROM megashedule""").fetchall()
        result = [str(item) for sub in pre_result for item in sub]
        con.commit()
        con.close()
        return result
        # Получение списка всех классов(чтобы не делать это вручную)

    def create_list_of_subjects(self):
        con = sqlite3.connect('timetable.db')
        cur = con.cursor()
        pre_result = cur.execute("""SELECT DISTINCT subject FROM megashedule""").fetchall()
        result = [str(item) for sub in pre_result for item in sub]
        con.commit()
        con.close()
        return result
        # Получение списка всех предметов(чтобы не делать это вручную)

    def create_class_subject_teacher_table(self):
        con = sqlite3.connect('timetable.db')
        cur = con.cursor()
        cur.execute("""DELETE FROM megashedule""")
        for e in megashedule:
            cur.execute("""INSERT INTO megashedule (class, subject, teacher) 
                            VALUES (?, ?, ?)""", e)
        result = cur.execute("""SELECT DISTINCT class, subject, teacher FROM megashedule""").fetchall()
        cur.execute("""DELETE FROM megashedule""")
        for e in result:
            cur.execute("""INSERT INTO megashedule (class, subject, teacher) 
                            VALUES (?, ?, ?)""", e)
        cur.execute("""DELETE FROM megashedule WHERE subject = ''""")
        con.commit()
        con.close()
        # Заполнение большой таблицы в SQL

    def get_value_for_parent(self, cl, sub):
        con = sqlite3.connect('timetable.db')
        cur = con.cursor()
        result = cur.execute("""SELECT room, teacher FROM {} WHERE lesson = ? AND teacher=(SELECT teacher
        FROM megashedule WHERE class = ? AND subject = ?)""".format(Timetable().get_today_day()),
                             (Timetable().get_today_lesson(), cl, sub)).fetchall()
        con.commit()
        con.close()
        try:
            return result[0][0], result[0][1]
        except IndexError:
            return 'на данный момент нет урока у учителя', 'проверьте в учительской'
        # Получение выходных данных для родителя с учетом ошибки

    def get_value_for_student(self, cl):
        con = sqlite3.connect('timetable.db')
        cur = con.cursor()
        result = cur.execute(
            """SELECT room, teacher FROM {} WHERE class = ? AND lesson = ?""".format(Timetable().get_today_day()),
            (cl, Timetable().get_today_lesson())).fetchall()
        con.commit()
        con.close()
        try:
            return result[0][0], result[0][1]
        except IndexError:
            return 'окно', ''
        # Получение выходных данных для ученика с учетом ошибки

    def get_today_day(self):
        now_table = ''
        if now.isoweekday() == 1:
            now_table = 'mon_shedule'
        elif now.isoweekday() == 2:
            now_table = 'tue_shedule'
        elif now.isoweekday() == 3:
            now_table = 'wed_shedule'
        elif now.isoweekday() == 4:
            now_table = 'thur_shedule'
        elif now.isoweekday() == 6:
            now_table = 'fri_shedule'
        return now_table
        # Получение сегодняшнего дня ориентируясь н реальное время

    def get_today_lesson(self):
        counter = 1
        for i in range(7):
            if Timetable().is_time_between(time(int(calls[0][i][0].split('.')[0]), int(calls[0][i][0].split('.')[1])),
                                           time(int(calls[0][i][1].split('.')[0]), int(calls[0][i][1].split('.')[1]))):
                return counter
            else:
                counter += 1
        # Получение данных о том, какой сейчас идет урок

    def is_time_between(self, begin_time, end_time):
        check_time = now.time()
        return check_time >= begin_time and check_time <= end_time
        # Определение находится ли во временном промежутке

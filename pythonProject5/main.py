import tkinter as tk
from tkinter import ttk
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import qrcode
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import random



class PatientDatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("База данных пациентов")

        # Подключение к базе данных MySQL
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="bdsanich"
        )
        self.cursor = self.connection.cursor()

        # Создание таблицы, если она не существует
        self.create_tables()

        # Создание и настройка элементов интерфейса
        self.create_widgets()

        # Загрузка данных из базы данных
        self.load_data()

        # Инициализация переменной для окна госпитализации
        self.hospitalization_window = None

    def create_tables(self):
        # Создание таблицы patients, если она не существует
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                patronymic VARCHAR(255),
                passport_series VARCHAR(20),
                passport_number VARCHAR(20),
                gender VARCHAR(10),
                date_of_birth DATE,
                insurance_number VARCHAR(20),
                insurance_expiry DATE,
                workplace VARCHAR(255)
            )
        """)
        # Создание таблицы hospitalizations, если она не существует
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospitalizations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                hospitalization_code VARCHAR(20),
                diagnosis TEXT,
                department VARCHAR(255),
                admission_conditions VARCHAR(255),
                admission_date DATETIME,
                discharge_date DATETIME,
                additional_info TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        """)
        self.connection.commit()

    def create_widgets(self):
        # Список пациентов
        self.patient_list = ttk.Treeview(self.root, columns=(
            "ID", "Имя", "Фамилия", "Отчество", "Серия паспорта", "Номер паспорта", "Место работы", "Пол",
            "Дата рождения",
            "Номер страхового полиса", "Дата окончания страхового полиса"))

        # Устанавливаем минимальную ширину для каждого столбца в Treeview
        self.patient_list.column("#0", width=45, anchor="center")
        self.patient_list.heading("#0", text="ID", anchor="center")

        self.patient_list.column("#1", width=100, anchor="center")
        self.patient_list.heading("#1", text="Имя", anchor="center")

        self.patient_list.column("#2", width=100, anchor="center")
        self.patient_list.heading("#2", text="Фамилия", anchor="center")

        self.patient_list.column("#3", width=100, anchor="center")
        self.patient_list.heading("#3", text="Отчество", anchor="center")

        self.patient_list.column("#4", width=100, anchor="center")
        self.patient_list.heading("#4", text="Серия паспорта", anchor="center")

        self.patient_list.column("#5", width=100, anchor="center")
        self.patient_list.heading("#5", text="Номер паспорта", anchor="center")

        self.patient_list.column("#6", width=100, anchor="center")
        self.patient_list.heading("#6", text="Место работы", anchor="center")

        self.patient_list.column("#7", width=100, anchor="center")
        self.patient_list.heading("#7", text="Пол", anchor="center")

        self.patient_list.column("#8", width=100, anchor="center")
        self.patient_list.heading("#8", text="Дата рождения", anchor="center")

        self.patient_list.column("#9", width=200, anchor="center")
        self.patient_list.heading("#9", text="Номер страхового полиса", anchor="center")

        self.patient_list.column("#10", width=220, anchor="center")
        self.patient_list.heading("#10", text="Дата окончания страхового полиса", anchor="center")

        self.patient_list.pack(padx=10, pady=10)

        # Кнопка "Добавить пациента"
        self.add_button = tk.Button(self.root, text="Добавить пациента", command=self.add_patient)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопка "Просмотр мед. карты"
        self.view_button = tk.Button(self.root, text="Просмотр мед. карты", command=self.view_medical_record)
        self.view_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопка "Госпитализация"
        self.hospitalization_button = tk.Button(self.root, text="Госпитализация", command=self.hospitalization)
        self.hospitalization_button.pack(side=tk.LEFT, padx=5, pady=5)

    def load_data(self):
        # Очистка списка пациентов перед загрузкой новых данных
        for record in self.patient_list.get_children():
            self.patient_list.delete(record)

        # Запрос данных из базы данных
        self.cursor.execute("SELECT * FROM patients")
        patients = self.cursor.fetchall()

        # Вставка данных в список пациентов
        for patient in patients:
            self.patient_list.insert("", "end", text=patient[0], values=(
                patient[1], patient[2], patient[3], patient[4], patient[5], patient[10], patient[6], patient[7],
                patient[8], patient[9]
            ))

    def add_patient(self):
        # Создание окна для ввода данных пациента
        self.add_patient_window = tk.Toplevel(self.root)
        self.add_patient_window.title("Добавить пациента")

        # Метки и поля для ввода данных
        tk.Label(self.add_patient_window, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.first_name_entry = tk.Entry(self.add_patient_window)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.add_patient_window, text="Фамилия:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.last_name_entry = tk.Entry(self.add_patient_window)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.add_patient_window, text="Отчество:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.patronymic_entry = tk.Entry(self.add_patient_window)
        self.patronymic_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.add_patient_window, text="Серия паспорта:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.passport_series_entry = tk.Entry(self.add_patient_window)
        self.passport_series_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.add_patient_window, text="Номер паспорта:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.passport_number_entry = tk.Entry(self.add_patient_window)
        self.passport_number_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self.add_patient_window, text="Место работы:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.workplace_entry = tk.Entry(self.add_patient_window)
        self.workplace_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(self.add_patient_window, text="Пол:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.gender_entry = tk.Entry(self.add_patient_window)
        self.gender_entry.grid(row=6, column=1, padx=5, pady=5)

        tk.Label(self.add_patient_window, text="Дата рождения:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.date_of_birth_entry = tk.Entry(self.add_patient_window)
        self.date_of_birth_entry.grid(row=7, column=1, padx=5, pady=5)

        tk.Label(self.add_patient_window, text="Номер страхового полиса:").grid(row=8, column=0, padx=5, pady=5,
                                                                                sticky="e")
        self.insurance_number_entry = tk.Entry(self.add_patient_window)
        self.insurance_number_entry.grid(row=8, column=1, padx=5, pady=5)

        tk.Label(self.add_patient_window, text="Дата окончания страхового полиса:").grid(row=9, column=0, padx=5,
                                                                                         pady=5, sticky="e")
        self.insurance_expiry_entry = tk.Entry(self.add_patient_window)
        self.insurance_expiry_entry.grid(row=9, column=1, padx=5, pady=5)

        # Кнопка "Добавить"
        tk.Button(self.add_patient_window, text="Добавить", command=self.save_patient).grid(row=10, column=0,
                                                                                            columnspan=2, padx=5,
                                                                                            pady=5)

    def save_patient(self):
        # Получение данных из полей ввода
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        patronymic = self.patronymic_entry.get()
        passport_series = self.passport_series_entry.get()
        passport_number = self.passport_number_entry.get()
        workplace = self.workplace_entry.get()
        gender = self.gender_entry.get()
        date_of_birth = self.date_of_birth_entry.get()
        insurance_number = self.insurance_number_entry.get()
        insurance_expiry = self.insurance_expiry_entry.get()

        # Вставка данных в базу данных
        sql = "INSERT INTO patients (first_name, last_name, patronymic, passport_series, passport_number, workplace, gender, date_of_birth, insurance_number, insurance_expiry) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (first_name, last_name, patronymic, passport_series, passport_number, workplace, gender, date_of_birth,
               insurance_number, insurance_expiry)
        self.cursor.execute(sql, val)
        self.connection.commit()

        # Обновление списка пациентов
        self.load_data()

        # Закрытие окна добавления пациента
        self.add_patient_window.destroy()

    def view_medical_record(self):
        # Функция для просмотра медицинской карты пациента
        selected_item = self.patient_list.focus()
        if not selected_item:
            print("Выберите пациента для просмотра медицинской карты.")
            return

        try:
            patient_id = self.patient_list.item(selected_item)["text"]
            self.cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
            patient_data = self.cursor.fetchone()

            # Создание PDF с медицинской картой
            pdf_filename = f"Medical_Record_Patient_{patient_id}.pdf"
            c = canvas.Canvas(pdf_filename, pagesize=letter)

            # Загрузка шрифтов Oswald-Bold и Oswald-Regular
            oswald_bold_path = "C:\\Users\\shers\\Desktop\\fonts\\Oswald-Bold.ttf"
            oswald_regular_path = "C:\\Users\\shers\\Desktop\\fonts\\Oswald-Regular.ttf"
            pdfmetrics.registerFont(TTFont('Oswald-Bold', oswald_bold_path))
            pdfmetrics.registerFont(TTFont('Oswald-Regular', oswald_regular_path))

            # Заголовок "Медицинская карта пациента"
            c.setFont("Oswald-Bold", 18)
            text_width = c.stringWidth("Медицинская карта пациента", "Oswald-Bold")  # Ширина текста
            c.drawString((letter[0] - text_width) / 2, 750, "Медицинская карта пациента")  # Центрирование текста

            # Данные пациента
            c.setFont("Oswald-Bold", 12)
            c.drawString(50, 700, "Имя:")
            c.setFont("Oswald-Regular", 12)
            c.drawString(85, 700, f"{patient_data[1]}")

            c.setFont("Oswald-Bold", 12)
            c.drawString(50, 680, "Фамилия:")
            c.setFont("Oswald-Regular", 12)
            c.drawString(110, 680, f"{patient_data[2]}")

            c.setFont("Oswald-Bold", 12)
            c.drawString(50, 660, "Отчество:")
            c.setFont("Oswald-Regular", 12)
            c.drawString(110, 660, f"{patient_data[3]}")

            c.setFont("Oswald-Bold", 12)
            c.drawString(50, 640, "Дата рождения:")
            c.setFont("Oswald-Regular", 12)
            c.drawString(140, 640, f"{patient_data[7]}")

            # Идентификационный код
            hospitalization_code = f"МК{random.randint(1, 100000)}"  # Генерация рандомного кода
            c.setFont("Oswald-Bold", 12)
            c.drawString(50, 720, f"Идентификационный код: {hospitalization_code}")

            # Генерация и вставка QR-кода
            qr_data = f"Имя: {patient_data[1]}, Фамилия: {patient_data[2]}, Дата рождения: {patient_data[7]}"
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img.save("temp_qr.png")
            qr_width, qr_height = qr_img.size
            c.drawInlineImage("temp_qr.png", (letter[0] - qr_width) / 2, 125)  # Позиционирование QR-кода

            c.save()
            print(f"Медицинская карта пациента {patient_id} успешно создана.")
        except Exception as e:
            print(f"Ошибка при создании медицинской карты: {e}")
        finally:
            self.root.focus_set()

    def hospitalization(self):
        # Создание окна для ввода кода госпитализации
        self.hospitalization_window = tk.Toplevel(self.root)
        self.hospitalization_window.title("Госпитализация")

        # Метка и поле для ввода кода госпитализации
        tk.Label(self.hospitalization_window, text="Введите код госпитализации:").pack()
        self.hospitalization_code_entry = tk.Entry(self.hospitalization_window)
        self.hospitalization_code_entry.pack()

        # Кнопка "Подтвердить госпитализацию"
        tk.Button(self.hospitalization_window, text="Подтвердить", command=self.confirm_hospitalization).pack()

    def confirm_hospitalization(self):
        # Закрытие окна ввода кода госпитализации
        self.hospitalization_window.destroy()

        # Отображение окна с сообщением об успешной госпитализации
        self.show_hospitalization_confirmation()

    def show_hospitalization_confirmation(self):
        # Создание окна с сообщением об успешной госпитализации
        self.hospitalization_confirmation_window = tk.Toplevel(self.root)
        self.hospitalization_confirmation_window.title("Госпитализация")

        # Текст сообщения об успешной госпитализации
        confirmation_text = "Пациент успешно госпитализирован."
        tk.Label(self.hospitalization_confirmation_window, text=confirmation_text).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = PatientDatabaseApp(root)
    root.mainloop()

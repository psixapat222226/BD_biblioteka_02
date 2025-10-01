"""
Модуль пользовательского интерфейса для приложения "Театральный менеджер".
Содержит классы для всех окон и диалогов приложения.
"""
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                              QHBoxLayout, QWidget, QDialog, QMessageBox, QComboBox,
                              QSpinBox, QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
                              QFormLayout, QTabWidget, QScrollArea, QFrame, QHeaderView, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QDate
from PySide6.QtGui import QFont, QIntValidator

from controller import TheaterController
from logger import Logger


# Add this class to the app.py file
class ValidatedLoginLineEdit(QLineEdit):
    """
    Поле ввода с валидацией для окна логина.
    Разрешает только определенные символы.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        """Обработка нажатия клавиш с валидацией."""
        # Сохраняем текущий текст и позицию курсора
        old_text = self.text()
        cursor_pos = self.cursorPosition()

        # Вызываем стандартную обработку нажатия клавиш
        super().keyPressEvent(event)

        # Проверяем валидность нового текста
        new_text = self.text()

        # Паттерн для проверки - разрешены буквы, цифры, некоторые спецсимволы
        import re
        pattern = r'^[а-яА-Яa-zA-Z0-9\s._-]*$'

        # Если текст пустой, разрешаем его
        if not new_text or re.match(pattern, new_text):
            return

        # Если текст не валиден, восстанавливаем старый текст
        self.setText(old_text)
        self.setCursorPosition(cursor_pos)


class LoginDialog(QDialog):
    """
    Диалог авторизации и подключения к базе данных.
    Позволяет ввести параметры подключения, создать БД или подключиться к существующей.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = TheaterController()
        self.logger = Logger()

        # Единый стиль для всех диалоговых окон сообщений
        self.message_box_style = """
            QMessageBox {
                background-color: #f5f5f5;
            }
            QMessageBox QLabel {
                color: #333333;
            }
            QMessageBox QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                min-width: 40px;
                min-height: 20px;
            }
            QMessageBox QPushButton:hover {
                background-color: #3a76d8;
            }
            QMessageBox QPushButton:pressed {
                background-color: #2a66c8;
            }
        """

        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса диалога."""
        self.setWindowTitle("Подключение к базе данных")
        self.setMinimumWidth(400)
        self.setModal(True)
        self.setStyleSheet("background-color: #f5f5f5;")

        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("Библиотека")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: green; ")
        layout.addWidget(title_label)

        # Форма для ввода параметров
        form_layout = QFormLayout()
        form_label_style = "color: #333333; font-weight: bold;"

        # Выбор базы данных
        self.db_combo = QComboBox()
        self.db_combo.addItem("task1")
        self.db_combo.addItem("task2")
        self.db_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 6px;
                min-height: 5px;
                min-width: 88px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #c0c0c0;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 10px;
                height: 10px;
                background: #4a86e8;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                background-color: white;
                color: black;
                selection-background-color: #d0e8ff;
                selection-color: black;
                padding: 4px;
            }
        """)
        db_label = QLabel("База данных:")
        db_label.setStyleSheet(form_label_style)
        form_layout.addRow(db_label, self.db_combo)

        # Поле для ввода хоста
        self.host_edit = ValidatedLoginLineEdit("localhost")
        self.host_edit.setStyleSheet("color: black;")
        host_label = QLabel("Хост:")
        host_label.setStyleSheet(form_label_style)
        form_layout.addRow(host_label, self.host_edit)

        # Поле для ввода порта
        self.port_edit = ValidatedLoginLineEdit("5432")
        self.port_edit.setStyleSheet("color: black;")
        self.port_edit.setValidator(QIntValidator(1, 65535))
        port_label = QLabel("Порт:")
        port_label.setStyleSheet(form_label_style)
        form_layout.addRow(port_label, self.port_edit)

        # Поле для ввода имени пользователя
        self.user_edit = ValidatedLoginLineEdit("postgres")
        self.user_edit.setStyleSheet("color: black;")
        user_label = QLabel("Пользователь:")
        user_label.setStyleSheet(form_label_style)
        form_layout.addRow(user_label, self.user_edit)

        # Поле для ввода пароля
        self.password_edit = QLineEdit("1234qwer")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("color: black;")
        password_label = QLabel("Пароль:")
        password_label.setStyleSheet(form_label_style)
        form_layout.addRow(password_label, self.password_edit)

        layout.addLayout(form_layout)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        button_style = """
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
        """

        # Кнопка подключения
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.clicked.connect(self.try_connect)
        self.connect_btn.setStyleSheet(button_style)
        buttons_layout.addWidget(self.connect_btn)

        # Кнопка создания БД
        self.create_db_btn = QPushButton("Создать БД")
        self.create_db_btn.clicked.connect(self.create_database)
        self.create_db_btn.setStyleSheet(button_style)
        buttons_layout.addWidget(self.create_db_btn)

        # Кнопка выхода
        self.exit_btn = QPushButton("Выход")
        self.exit_btn.clicked.connect(self.reject)
        self.exit_btn.setStyleSheet(button_style)
        buttons_layout.addWidget(self.exit_btn)

        layout.addLayout(buttons_layout)

    def try_connect(self):
        """Попытка подключения к базе данных с введенными параметрами."""
        # Получение параметров из полей ввода
        dbname = self.db_combo.currentText()
        host = self.host_edit.text()
        port = self.port_edit.text()
        user = self.user_edit.text()
        password = self.password_edit.text()

        # Проверка заполнения всех обязательных полей
        if not dbname or not host or not port or not user:
            warn_box = QMessageBox(self)
            warn_box.setWindowTitle("Ошибка")
            warn_box.setText("Все поля, кроме пароля, должны быть заполнены")
            warn_box.setIcon(QMessageBox.Warning)
            warn_box.setStyleSheet(self.message_box_style)
            warn_box.exec()
            return

        # Установка параметров подключения
        self.controller.set_connection_params(dbname, user, password, host, port)

        # Попытка подключения
        if self.controller.connect_to_database():
            try:
                # Проверка существования структуры базы данных
                self.controller.db.cursor.execute(
                    "SELECT 1 FROM information_schema.tables WHERE table_name = 'books'")
                table_exists = self.controller.db.cursor.fetchone() is not None

                # Если структура не существует, предлагаем создать
                if not table_exists:
                    reply_box = QMessageBox(self)
                    reply_box.setWindowTitle("Схема не найдена")
                    reply_box.setText("Структура базы данных не найдена. Схемы и таблицы будут созданы")
                    reply_box.setIcon(QMessageBox.Information)
                    reply_box.setStyleSheet(self.message_box_style)
                    reply = reply_box.exec()

                    # Создание схемы и таблиц
                    if self.controller.initialize_database():
                        ok_box = QMessageBox(self)
                        ok_box.setWindowTitle("Успех")
                        ok_box.setText("Схема и таблицы успешно созданы")
                        ok_box.setIcon(QMessageBox.Information)
                        ok_box.setStyleSheet(self.message_box_style)
                        ok_box.exec()
                    else:
                        err_box = QMessageBox(self)
                        err_box.setWindowTitle("Ошибка")
                        err_box.setText("Не удалось создать схему базы данных")
                        err_box.setIcon(QMessageBox.Critical)
                        err_box.setStyleSheet(self.message_box_style)
                        err_box.exec()
                        return

                # Подключение успешно
                success_box = QMessageBox(self)
                success_box.setWindowTitle("Успех")
                success_box.setText("Подключение успешно установлено")
                success_box.setIcon(QMessageBox.Information)
                success_box.setStyleSheet(self.message_box_style)
                success_box.exec()
                self.accept()

            except Exception as e:
                # Ошибка при проверке структуры БД
                err_box = QMessageBox(self)
                err_box.setWindowTitle("Ошибка")
                err_box.setText(f"Ошибка при проверке структуры базы данных: {str(e)}")
                err_box.setIcon(QMessageBox.Critical)
                err_box.setStyleSheet(self.message_box_style)
                err_box.exec()
        else:
            # Ошибка подключения к БД
            err_box = QMessageBox(self)
            err_box.setWindowTitle("Ошибка")
            err_box.setText("Не удалось подключиться к базе данных. Проверьте параметры подключения.")
            err_box.setIcon(QMessageBox.Critical)
            err_box.setStyleSheet(self.message_box_style)
            err_box.exec()

    def create_database(self):
        """Создание новой базы данных с введенными параметрами."""
        # Получение параметров из полей ввода
        dbname = self.db_combo.currentText()
        host = self.host_edit.text()
        port = self.port_edit.text()
        user = self.user_edit.text()
        password = self.password_edit.text()

        # Проверка заполнения всех обязательных полей
        if not dbname or not host or not port or not user:
            warn_box = QMessageBox(self)
            warn_box.setWindowTitle("Ошибка")
            warn_box.setText("Все поля, кроме пароля, должны быть заполнены")
            warn_box.setIcon(QMessageBox.Warning)
            warn_box.setStyleSheet(self.message_box_style)
            warn_box.exec()
            return

        # Установка параметров подключения
        self.controller.set_connection_params(dbname, user, password, host, port)

        # Попытка создания базы данных
        if self.controller.create_database():
            # Запрос на создание схемы и таблиц
            reply_box = QMessageBox(self)
            reply_box.setWindowTitle("База данных создана")
            reply_box.setText("База данных успешно создана. Хотите создать схемы и таблицы?")
            reply_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            reply_box.setIcon(QMessageBox.Question)
            reply_box.setStyleSheet(self.message_box_style)
            reply = reply_box.exec()

            if reply == QMessageBox.Yes:
                # Подключение и инициализация базы данных
                if self.controller.connect_to_database() and self.controller.initialize_database():
                    success_box = QMessageBox(self)
                    success_box.setWindowTitle("Успех")
                    success_box.setText("База данных, схема и таблицы успешно созданы")
                    success_box.setIcon(QMessageBox.Information)
                    success_box.setStyleSheet(self.message_box_style)
                    success_box.exec()
                    self.accept()
                else:
                    err_box = QMessageBox(self)
                    err_box.setWindowTitle("Ошибка")
                    err_box.setText("Не удалось создать схему базы данных")
                    err_box.setIcon(QMessageBox.Critical)
                    err_box.setStyleSheet(self.message_box_style)
                    err_box.exec()
            else:
                # Пользователь отказался создавать схемы и таблицы
                return
        else:
            # Ошибка создания базы данных
            err_box = QMessageBox(self)
            err_box.setWindowTitle("Ошибка")
            err_box.setText("Не удалось создать базу данных")
            err_box.setIcon(QMessageBox.Critical)
            err_box.setStyleSheet(self.message_box_style)
            err_box.exec()


class MainWindow(QMainWindow):
    """
    Главное окно приложения "Библиотека".
    Содержит все основные функции управления библиотекой.
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.logger = Logger()

        self.setWindowTitle("Библиотека")
        self.setMinimumSize(900, 600)

        # Установка стилей для всего приложения
        self.set_application_style()

        # Инициализация интерфейса
        self.setup_ui()

        # Загрузка логов и обновление информации
        self.load_logs()


        self.logger.info("Главное окно инициализировано")

    def setup_ui(self):
        """Настройка пользовательского интерфейса главного окна."""
        # Создание центрального виджета
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        # Заголовок
        title_label = QLabel("Библиотека")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: green; margin: 10px;")
        main_layout.addWidget(title_label)

        # Панель кнопок
        self.setup_buttons(main_layout)



        # Создание вкладок для логов и других данных
        self.data_tabs = QTabWidget()
        main_layout.addWidget(self.data_tabs)

        # Вкладка логов
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: black; color: green; ")
        log_layout.addWidget(self.log_display)
        self.data_tabs.addTab(log_tab, "Логи")
        self.data_tabs.setCurrentIndex(0)

        # Регистрация дисплея логов в логгере
        self.logger.set_main_window_log_display(self.log_display)

        # Кнопки управления внизу
        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addStretch()
        self.reset_db_btn = QPushButton("Обновить данные")
        self.reset_db_btn.clicked.connect(self.reset_database)
        bottom_btn_layout.addWidget(self.reset_db_btn)

        self.reset_schema_btn = QPushButton("Обновить схему")
        self.reset_schema_btn.clicked.connect(self.reset_schema)
        bottom_btn_layout.addWidget(self.reset_schema_btn)

        # Кнопка отключения от БД
        self.disconnect_btn = QPushButton("Отключиться от БД")
        self.disconnect_btn.setFixedWidth(160)
        self.disconnect_btn.clicked.connect(self.disconnect_from_db)
        bottom_btn_layout.addWidget(self.disconnect_btn)
        bottom_btn_layout.addStretch()
        main_layout.addLayout(bottom_btn_layout)

    def setup_buttons(self, main_layout):
        """Настройка панели кнопок главного окна."""
        buttons_layout = QHBoxLayout()

        # Кнопка просмотра таблицы Авторы
        self.authors_btn = QPushButton("Авторы")
        self.authors_btn.clicked.connect(self.show_authors)
        buttons_layout.addWidget(self.authors_btn)

        # Кнопка просмотра таблицы Книги
        self.books_btn = QPushButton("Книги")
        self.books_btn.clicked.connect(self.show_books)
        buttons_layout.addWidget(self.books_btn)

        # Кнопка просмотра таблицы Читатели
        self.readers_btn = QPushButton("Читатели")
        self.readers_btn.clicked.connect(self.show_readers)
        buttons_layout.addWidget(self.readers_btn)

        # Кнопка просмотра таблицы Заказы но пока читатели
        self.issues_btn = QPushButton("Заказы")
        self.issues_btn.clicked.connect(self.show_issues)
        buttons_layout.addWidget(self.issues_btn)

        # Кнопка просмотра таблицы тоже в разработке
        self.books_authors_btn = QPushButton("Автор/книга")
        self.books_authors_btn.clicked.connect(self.show_books_authors)
        buttons_layout.addWidget(self.books_authors_btn)

        main_layout.addLayout(buttons_layout)

    def load_logs(self):
        """Загрузка содержимого лог-файла в окно логов."""
        try:
            with open("app.log", "r", encoding="utf-8") as f:
                log_content = f.read()
                self.log_display.setText(log_content)

            # Прокрутка к последней записи
            QTimer.singleShot(100, lambda: self.log_display.verticalScrollBar().setValue(
                self.log_display.verticalScrollBar().maximum()))
        except Exception as e:
            self.logger.error(f"Ошибка загрузки логов: {str(e)}")

    def append_log(self, message):
        """Добавление сообщения в окно логов с прокруткой вниз."""
        if hasattr(self, 'log_display') and self.log_display is not None:
            self.log_display.append(message)
            # Прокрутка вниз для отображения новых сообщений
            scrollbar = self.log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def set_application_style(self):
        """Установка единого стиля для всего приложения."""
        app_style = """
        QMainWindow, QDialog {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: green;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2E6F40;
        }
        QPushButton:pressed {
            background-color: #2E6F40;
        }
        QLabel {
            color: #333333;
        }
        QTableWidget {
            border: 1px solid #d0d0d0;
            gridline-color: #e0e0e0;
        }
        QTableWidget::item:selected {
            background-color: #d0e8ff;
        }
        QHeaderView::section {
            background-color: #e0e0e0;
            color: #333333;
            padding: 4px;
            border: 1px solid #c0c0c0;
            font-weight: bold;
        }
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #333333;
            padding: 8px 12px;
            border: 1px solid #c0c0c0;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: white;
            font-weight: bold;
        }
        QComboBox {
            background-color: white;
            color: #333333;
            border: 1px solid #c0c0c0;
            border-radius: 4px;
            padding: 6px;
            min-height: 25px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #c0c0c0;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        QComboBox::down-arrow {
            image: none;
            width: 10px;
            height: 10px;
            background: #4a86e8;
            border-radius: 5px;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #c0c0c0;
            border-radius: 4px;
            background-color: white;
            color: #333333;
            selection-background-color: #d0e8ff;
            selection-color: #333333;
            padding: 4px;
        }
        QLineEdit {
            background-color: white;
            color: #333333;
            border: 1px solid #c0c0c0;
            padding: 4px;
            min-width: 120px;
        }
        QTextEdit {
            border: 1px solid #c0c0c0;
            padding: 2px;
        }
        QSpinBox {
            background-color: white;
            color: #333333;
            border: 1px solid #c0c0c0;
            border-radius: 4px;
            padding: 1px 1px 1px 4px;
            min-width: 80px;
            max-height: 22px;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #e8e8e8;
            width: 16px;
            border: none;
            border-left: 1px solid #c0c0c0;
        }
        QSpinBox::up-button {
            border-top-right-radius: 3px;
            border-bottom: 1px solid #c0c0c0;
        }
        QSpinBox::down-button {
            border-bottom-right-radius: 3px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #d0e8ff;
        }
        QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
            background-color: #4a86e8;
        }
        QSpinBox::up-arrow, QSpinBox::down-arrow {
            width: 6px;
            height: 6px;
            background: #4a86e8;
        }
        QSpinBox:focus {
            border: 1px solid #4a86e8;
        }
        
        """

        self.setStyleSheet(app_style)



    def reset_database(self):
        """Сброс данных базы данных к начальному состоянию."""
        # Запрос подтверждения
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите обновить все данные к начальному состоянию?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Сброс базы данных
            result = self.controller.reset_database()
            if result:
                QMessageBox.information(self, "Успех", "Данные успешно обновлены")

            else:
                QMessageBox.critical(self, "Ошибка",
                                     "Не удалось обновить данные. Проверьте логи для получения подробной информации.")

    def reset_schema(self):
        """Сброс схемы базы данных (удаление и пересоздание всех таблиц)."""
        # Запрос подтверждения
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите полностью обновить схему базы данных? Все данные будут удалены.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Сброс схемы
            result = self.controller.reset_schema()
            if result:
                QMessageBox.information(self, "Успех", "Схема базы данных успешно обновлена.")

            else:
                QMessageBox.critical(self, "Ошибка",
                                     "Не удалось обновить схему базы данных. Проверьте логи для получения подробной информации.")



    def show_authors(self):
        """Открытие диалога просмотра таблицы авторов"""
        dialog = AuthorsDialog(self.controller, self)
        dialog.exec()

    def show_readers(self):
        """Открытие диалога просмотра таблицы читателей."""
        dialog = ReadersDialog(self.controller, self)
        dialog.exec()

    def show_books(self):
        """Открытие диалога просмотра таблицы книг"""
        dialog = BooksDialog(self.controller, self)
        dialog.exec()

    def show_issues(self):
        """Открытие диалога просмотра таблицы заказов"""
        dialog = IssuesDialog(self.controller, self)
        dialog.exec()

    def show_books_authors(self):
        """Открытие диалога просмотра таблицы связи книг и авторов"""
        pass
        dialog = BookAuthorsDialog(self.controller, self)
        dialog.exec()

    def disconnect_from_db(self):
        """Отключение от базы данных и выход из программы."""
        # Запрос подтверждения
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите отключиться от базы данных и выйти из программы?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.logger.info("Отключение от базы данных и выход из программы")
            self.controller.close()
            self.close()

    def closeEvent(self, event):
        """Обработка события закрытия окна."""
        self.controller.close()
        event.accept()


# Вспомогательные классы для таблиц

class NumericTableItem(QTableWidgetItem):
    """
    Элемент таблицы для числовых значений с правильной сортировкой.
    """

    def __init__(self, text, value):
        super().__init__(text)
        self.value = value

    def __lt__(self, other):
        """Сравнение по числовому значению, а не по тексту."""
        if hasattr(other, 'value'):
            return self.value < other.value
        return super().__lt__(other)


class RankTableItem(QTableWidgetItem):
    """
    Элемент таблицы для званий актеров с правильной сортировкой.
    """

    def __init__(self, text):
        super().__init__(text)
        rank_order = ['Начинающий', 'Постоянный', 'Ведущий', 'Мастер', 'Заслуженный', 'Народный']
        self.rank_index = rank_order.index(text) if text in rank_order else -1

    def __lt__(self, other):
        """Сравнение по порядку званий, а не по алфавиту."""
        if isinstance(other, RankTableItem):
            return self.rank_index < other.rank_index
        return super().__lt__(other)


class CurrencyTableItem(QTableWidgetItem):
    """
    Элемент таблицы для денежных значений с правильной сортировкой.
    """

    def __init__(self, text, value):
        super().__init__(text)
        self.value = value

    def __lt__(self, other):
        """Сравнение по числовому значению, а не по тексту."""
        if hasattr(other, 'value'):
            return self.value < other.value
        return super().__lt__(other)


class ValidatedLineEdit(QLineEdit):
    """
    Поле ввода с валидацией текста.
    Разрешает только определенные символы, заданные в контроллере.
    """

    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller

    def keyPressEvent(self, event):
        """Обработка нажатия клавиш с валидацией."""
        # Сохраняем текущий текст и позицию курсора
        old_text = self.text()
        cursor_pos = self.cursorPosition()

        # Вызываем стандартную обработку нажатия клавиш
        super().keyPressEvent(event)

        # Проверяем валидность нового текста
        new_text = self.text()

        # Если текст пустой, разрешаем его
        if not new_text or self.controller.is_valid_text_input(new_text):
            return

        # Если текст не валиден, восстанавливаем старый текст
        self.setText(old_text)
        self.setCursorPosition(cursor_pos)

class AddAuthorDialog(QDialog):
    """
    Диалог добавления нового автора.
    Позволяет ввести ФИО, год рождения (удобно через QSpinBox) и выбрать страну из списка.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Добавить автора")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = "color: #333333; font-weight: bold;"

        # Фамилия
        last_name_label = QLabel("Фамилия:")
        last_name_label.setStyleSheet(label_style)
        self.last_name_edit = QLineEdit()
        layout.addRow(last_name_label, self.last_name_edit)

        # Имя
        first_name_label = QLabel("Имя:")
        first_name_label.setStyleSheet(label_style)
        self.first_name_edit = QLineEdit()
        layout.addRow(first_name_label, self.first_name_edit)

        # Отчество
        patronymic_label = QLabel("Отчество:")
        patronymic_label.setStyleSheet(label_style)
        self.patronymic_edit = QLineEdit()
        layout.addRow(patronymic_label, self.patronymic_edit)

        # Год рождения через QSpinBox (аналогично year_spin)
        birth_year_label = QLabel("Год рождения:")
        birth_year_label.setStyleSheet(label_style)
        self.birth_year_spin = QSpinBox()
        self.birth_year_spin.setRange(1700, 2025)
        self.birth_year_spin.setValue(1980)
        layout.addRow(birth_year_label, self.birth_year_spin)

        # Страна через QComboBox (выбор из списка)
        country_label = QLabel("Страна:")
        country_label.setStyleSheet(label_style)
        self.country_combo = QComboBox()
        # Список стран (можно расширить по необходимости)
        countries = [
            "Россия", "Великобритания", "США", "Франция", "Германия", "Италия",
            "Китай", "Япония", "Испания", "Польша", "Чехия", "Украина", "Беларусь",
            "Казахстан", "Канада", "Австралия", "Швеция", "Нидерланды", "Другая"
        ]
        self.country_combo.addItems(countries)
        layout.addRow(country_label, self.country_combo)

        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        if not self.last_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите фамилию автора")
            return
        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя автора")
            return
        # birth_year_spin всегда выдаёт int, так что отдельно проверять необязательно
        if not self.country_combo.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Выберите страну автора")
            return
        self.accept()

class AddBookDialog(QDialog):
    """
    Диалог добавления новой книги.
    Позволяет ввести название, год издания (QSpinBox), выбрать жанр из списка,
    ввести ISBN и количество экземпляров (QSpinBox).
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Добавить книгу")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = "color: #333333; font-weight: bold;"

        # Название
        title_label = QLabel("Название:")
        title_label.setStyleSheet(label_style)
        self.title_edit = QLineEdit()
        layout.addRow(title_label, self.title_edit)

        # Год издания
        year_label = QLabel("Год издания:")
        year_label.setStyleSheet(label_style)
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1450, 2025)
        self.year_spin.setValue(2000)
        layout.addRow(year_label, self.year_spin)

        # Жанр через QComboBox (выбор из списка)
        genre_label = QLabel("Жанр:")
        genre_label.setStyleSheet(label_style)
        self.genre_combo = QComboBox()
        genres = [
            "Роман", "Фантастика", "Детектив", "Поэзия", "Научная литература",
            "Биография", "Исторический роман", "Приключения", "Документальная",
            "Драма", "Триллер", "Детская литература", "Сказка", "Комедия",
            "Фэнтези", "Манга", "Психология", "Бизнес", "Другое"
        ]
        self.genre_combo.addItems(genres)
        layout.addRow(genre_label, self.genre_combo)

        # ISBN
        isbn_label = QLabel("ISBN:")
        isbn_label.setStyleSheet(label_style)
        self.isbn_edit = QLineEdit()
        layout.addRow(isbn_label, self.isbn_edit)

        # Количество экземпляров через QSpinBox
        copies_label = QLabel("Экземпляров:")
        copies_label.setStyleSheet(label_style)
        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(1, 9999)
        self.copies_spin.setValue(1)
        layout.addRow(copies_label, self.copies_spin)

        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название книги")
            return
        # year_spin всегда возвращает int, дополнительная проверка не нужна
        if not self.genre_combo.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Выберите жанр книги")
            return
        if not self.isbn_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите ISBN книги")
            return
        if int(self.copies_spin.value()) < 1:
            QMessageBox.warning(self, "Ошибка", "Количество экземпляров должно быть положительным")
            return
        self.accept()

class AuthorsDialog(QDialog):
    """
    Диалог для просмотра авторов.
    Отображает список всех свторов с возможностью добавления и удаления.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.parent_window = parent
        self.setWindowTitle("Авторы")
        self.setMinimumSize(800, 500)
        self.setup_ui()

    def edit_author(self, row, column):
        author_id = int(self.author_table.item(row, 0).text())
        author = next((p for p in self.authors if p['author_id'] == author_id), None)
        if not author:
            return
        dialog = EditAuthorDialog(self.controller, author, self)
        if dialog.exec():
            new_last_name = dialog.last_name_edit.text().strip()
            new_first_name = dialog.first_name_edit.text().strip()
            new_patronymic = dialog.patronymic_edit.text().strip()
            new_birth_year = int(dialog.birth_year_edit.text().strip())
            new_country = dialog.country_combo.currentText().strip()

            success, msg = self.controller.update_author(
                author_id,
                new_last_name,
                new_first_name,
                new_patronymic,
                new_birth_year,
                new_country
            )
            if success:
                self.update_authors_table()
                QMessageBox.information(self, "Успех", "Автор успешно обновлен.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить автора: {msg}")
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title_label = QLabel("<h2>Авторы</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        self.authors = self.controller.get_all_authors()
        if not self.authors:
            empty_label = QLabel("Авторов нет.")
            empty_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty_label)
        else:
            self.author_table = QTableWidget()
            self.author_table.setColumnCount(6)
            self.author_table.setHorizontalHeaderLabels(
                ["ID", "Фамилия", "Имя", "Отчество", "Год рождения", "Страна"])
            self.author_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.author_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.update_authors_table()
            self.author_table.setSortingEnabled(True)
            self.author_table.cellDoubleClicked.connect(self.edit_author)
            layout.addWidget(self.author_table)
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить автора")
        add_btn.clicked.connect(self.add_author)
        buttons_layout.addWidget(add_btn)
        del_btn = QPushButton("Удалить автора")
        del_btn.clicked.connect(self.delete_author)
        buttons_layout.addWidget(del_btn)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)

    def update_authors_table(self):
        self.authors = self.controller.get_all_authors()
        self.author_table.setRowCount(len(self.authors))
        for i, auth in enumerate(self.authors):
            id_item = NumericTableItem(str(auth['author_id']), auth['author_id'])
            last_name_item = QTableWidgetItem(auth['last_name'])
            first_name_item = QTableWidgetItem(auth['first_name'])
            patronymic_item = QTableWidgetItem(auth['patronymic'])
            year_item = NumericTableItem(str(auth['birth_year']), auth['birth_year'])
            country_item = QTableWidgetItem(auth['country'])
            self.author_table.setItem(i, 0, id_item)
            self.author_table.setItem(i, 1, last_name_item)
            self.author_table.setItem(i, 2, first_name_item)
            self.author_table.setItem(i, 3, patronymic_item)
            self.author_table.setItem(i, 4, year_item)
            self.author_table.setItem(i, 5, country_item)

    def add_author(self):
        dialog = AddAuthorDialog(self.controller, self)
        if dialog.exec():
            last_name = dialog.last_name_edit.text().strip()
            first_name = dialog.first_name_edit.text().strip()
            patronymic = dialog.patronymic_edit.text().strip()
            birth_year = dialog.birth_year_spin.value()
            country = dialog.country_combo.currentText().strip()
            success = self.controller.add_new_author(
                last_name,
                first_name,
                patronymic,
                birth_year,
                country
            )
            if success:
                self.update_authors_table()
                QMessageBox.information(self, "Успех", "Автор успешно добавлен")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить автора")

    def delete_author(self):
        selected_rows = self.author_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите автора для удаления.")
            return
        row = selected_rows[0].row()
        author_id = int(self.author_table.item(row, 0).text())
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить этого автора?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            success, msg = self.controller.delete_author_by_id(author_id)
            if success:
                self.update_authors_table()
                QMessageBox.information(self, "Успех", "Автор успешно удален")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить автора: {msg}")

class EditBookDialog(QDialog):
    """
    Диалог редактирования данных книги.
    """
    def __init__(self, controller, book, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.book = book

        self.setWindowTitle("Редактировать книгу")
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = "color: #333333; font-weight: bold;"

        # Название
        title_label = QLabel("Название:")
        title_label.setStyleSheet(label_style)
        self.title_edit = QLineEdit(self.book['title'])
        layout.addRow(title_label, self.title_edit)

        # Год издания
        year_label = QLabel("Год издания:")
        year_label.setStyleSheet(label_style)
        self.year_edit = QLineEdit(str(self.book['publication_year']))
        layout.addRow(year_label, self.year_edit)

        # Жанр (QComboBox)
        genre_label = QLabel("Жанр:")
        genre_label.setStyleSheet(label_style)
        self.genre_combo = QComboBox()
        genres = [
            "Роман", "Фантастика", "Детектив", "Поэзия", "Научная литература",
            "Биография", "Исторический роман", "Приключения", "Документальная",
            "Драма", "Триллер", "Детская литература", "Сказка", "Комедия",
            "Фэнтези", "Манга", "Психология", "Бизнес", "Другое"
        ]
        self.genre_combo.addItems(genres)
        if self.book['genre'] in genres:
            self.genre_combo.setCurrentText(self.book['genre'])
        else:
            self.genre_combo.addItem(self.book['genre'])
            self.genre_combo.setCurrentText(self.book['genre'])
        layout.addRow(genre_label, self.genre_combo)

        # ISBN
        isbn_label = QLabel("ISBN:")
        isbn_label.setStyleSheet(label_style)
        self.isbn_edit = QLineEdit(self.book['isbn'])
        layout.addRow(isbn_label, self.isbn_edit)

        # Количество экземпляров
        copies_label = QLabel("Экземпляров:")
        copies_label.setStyleSheet(label_style)
        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(0, 9999)
        self.copies_spin.setValue(self.book['available_copies'] if self.book['available_copies'] is not None else 1)
        layout.addRow(copies_label, self.copies_spin)

        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название книги")
            return

        year_text = self.year_edit.text().strip()
        if not year_text.isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите корректный год издания")
            return

        year = int(year_text)
        from datetime import datetime
        current_year = datetime.now().year

        if year < 1450 or year > current_year:
            QMessageBox.warning(
                self, "Ошибка",
                f"Год издания должен быть от 1450 до {current_year}"
            )
            return

        if not self.genre_combo.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Выберите жанр книги")
            return
        if not self.isbn_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите ISBN книги")
            return
        if int(self.copies_spin.value()) < 0:
            QMessageBox.warning(self, "Ошибка", "Количество экземпляров должно быть положительным")
            return

        self.accept()

class BooksDialog(QDialog):
    """
    Диалог для просмотра книг.
    Отображает список всех книг с возможностью добавления, редактирования и удаления.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.parent_window = parent
        self.setWindowTitle("Книги")
        self.setMinimumSize(900, 500)
        self.setup_ui()

    def edit_book(self, row, column):
        book_id = int(self.books_table.item(row, 0).text())
        book = next((b for b in self.books if b['book_id'] == book_id), None)
        if not book:
            return
        dialog = EditBookDialog(self.controller, book, self)
        if dialog.exec():
            new_title = dialog.title_edit.text().strip()
            new_year = int(dialog.year_edit.text().strip())
            new_genre = dialog.genre_combo.currentText()
            new_isbn = dialog.isbn_edit.text().strip()
            new_copies = int(dialog.copies_spin.value())

            success, msg = self.controller.update_book(
                book_id,
                new_title,
                new_year,
                new_genre,
                new_isbn,
                new_copies
            )
            if success:
                self.update_books_table()
                QMessageBox.information(self, "Успех", "Книга успешно обновлена.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить книгу: {msg}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        title_label = QLabel("<h2>Книги</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        self.books = self.controller.get_all_books()
        if not self.books:
            empty_label = QLabel("Книг нет.")
            empty_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty_label)
        else:
            self.books_table = QTableWidget()
            self.books_table.setColumnCount(6)
            self.books_table.setHorizontalHeaderLabels(
                ["ID", "Название", "Год издания", "Жанр", "ISBN", "Экземпляров"])
            self.books_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.books_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.update_books_table()
            self.books_table.setSortingEnabled(True)
            self.books_table.cellDoubleClicked.connect(self.edit_book)
            layout.addWidget(self.books_table)
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить книгу")
        add_btn.clicked.connect(self.add_book)
        buttons_layout.addWidget(add_btn)
        del_btn = QPushButton("Удалить книгу")
        del_btn.clicked.connect(self.delete_book)
        buttons_layout.addWidget(del_btn)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)

    def update_books_table(self):
        self.books = self.controller.get_all_books()
        self.books_table.setRowCount(len(self.books))
        for i, book in enumerate(self.books):
            id_item = NumericTableItem(str(book['book_id']), book['book_id'])
            title_item = QTableWidgetItem(book['title'])
            year_item = QTableWidgetItem(str(book['publication_year']) if book['publication_year'] is not None else "")
            genre_item = QTableWidgetItem(book['genre'] if book['genre'] else "")
            isbn_item = QTableWidgetItem(book['isbn'] if book['isbn'] else "")
            copies_item = QTableWidgetItem(str(book['available_copies']) if book['available_copies'] is not None else "0")
            self.books_table.setItem(i, 0, id_item)
            self.books_table.setItem(i, 1, title_item)
            self.books_table.setItem(i, 2, year_item)
            self.books_table.setItem(i, 3, genre_item)
            self.books_table.setItem(i, 4, isbn_item)
            self.books_table.setItem(i, 5, copies_item)

    def add_book(self):
        dialog = AddBookDialog(self.controller, self)
        if dialog.exec():
            title = dialog.title_edit.text().strip()
            year = int(dialog.year_spin.value())
            genre = dialog.genre_combo.currentText()
            isbn = dialog.isbn_edit.text().strip()
            copies = int(dialog.copies_spin.value())
            success = self.controller.add_new_book(
                title,
                year,
                genre,
                isbn,
                copies
            )
            if success:
                self.update_books_table()
                QMessageBox.information(self, "Успех", "Книга успешно добавлена")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить книгу")

    def delete_book(self):
        selected_rows = self.books_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для удаления.")
            return
        row = selected_rows[0].row()
        book_id = int(self.books_table.item(row, 0).text())
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить эту книгу?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            success, msg = self.controller.delete_book_by_id(book_id)
            if success:
                self.update_books_table()
                QMessageBox.information(self, "Успех", "Книга успешно удалена")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить книгу: {msg}")

class EditAuthorDialog(QDialog):
    """
    Диалог редактирования данных автора.
    """
    def __init__(self, controller, author, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.author = author

        self.setWindowTitle("Редактировать автора")
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = "color: #333333; font-weight: bold;"

        # Фамилия
        last_name_label = QLabel("Фамилия:")
        last_name_label.setStyleSheet(label_style)
        self.last_name_edit = QLineEdit(self.author['last_name'])
        layout.addRow(last_name_label, self.last_name_edit)

        # Имя
        first_name_label = QLabel("Имя:")
        first_name_label.setStyleSheet(label_style)
        self.first_name_edit = QLineEdit(self.author['first_name'])
        layout.addRow(first_name_label, self.first_name_edit)

        # Отчество
        patronymic_label = QLabel("Отчество:")
        patronymic_label.setStyleSheet(label_style)
        self.patronymic_edit = QLineEdit(self.author['patronymic'])
        layout.addRow(patronymic_label, self.patronymic_edit)

        # Год рождения
        birth_year_label = QLabel("Год рождения:")
        birth_year_label.setStyleSheet(label_style)
        self.birth_year_edit = QLineEdit(str(self.author['birth_year']))
        layout.addRow(birth_year_label, self.birth_year_edit)

        # Страна (QComboBox)
        country_label = QLabel("Страна:")
        country_label.setStyleSheet(label_style)
        self.country_combo = QComboBox()
        # Пример списка стран (можешь заменить на свой)
        countries = [
            "Россия", "Великобритания", "США", "Франция", "Германия", "Италия",
            "Китай", "Япония", "Испания", "Польша", "Чехия", "Украина", "Беларусь",
            "Казахстан", "Канада", "Австралия", "Швеция", "Нидерланды", "Другая"
        ]
        self.country_combo.addItems(countries)
        # Установить текущую страну автора, если она есть в списке
        if self.author['country'] in countries:
            self.country_combo.setCurrentText(self.author['country'])
        else:
            self.country_combo.addItem(self.author['country'])
            self.country_combo.setCurrentText(self.author['country'])
        layout.addRow(country_label, self.country_combo)

        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        if not self.last_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите фамилию автора")
            return
        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя автора")
            return

        birth_year_text = self.birth_year_edit.text().strip()
        if not birth_year_text.isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите корректный год рождения")
            return

        birth_year = int(birth_year_text)
        from datetime import datetime
        current_year = datetime.now().year

        # Ограничения: не раньше 1890 и не позже текущего года
        if birth_year < 1200 or birth_year > current_year:
            QMessageBox.warning(
                self, "Ошибка",
                f"Год рождения должен быть от 1200 до {current_year}"
            )
            return

        if not self.country_combo.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Выберите страну автора")
            return
        self.accept()

class EditReaderDialog(QDialog):
    """
    Диалог редактирования данных читателя.
    Позволяет изменить ФИО, звание, количество наград и опыт.
    """
    def __init__(self, controller, reader, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.reader = reader

        self.setWindowTitle("Редактировать данные читателя")
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса диалога."""
        layout = QFormLayout(self)

        # Стиль для меток
        label_style = "color: #333333; font-weight: bold;"

        # Поля для ввода данных читателя
        # Фамилия
        last_name_label = QLabel("Фамилия:")
        last_name_label.setStyleSheet(label_style)
        self.last_name_edit = ValidatedLineEdit(self.controller, self.reader['last_name'])
        layout.addRow(last_name_label, self.last_name_edit)

        # Имя
        first_name_label = QLabel("Имя:")
        first_name_label.setStyleSheet(label_style)
        self.first_name_edit = ValidatedLineEdit(self.controller, self.reader['first_name'])
        layout.addRow(first_name_label, self.first_name_edit)

        # Отчество
        patronymic_label = QLabel("Отчество:")
        patronymic_label.setStyleSheet(label_style)
        self.patronymic_edit = ValidatedLineEdit(self.controller, self.reader['patronymic'])
        layout.addRow(patronymic_label, self.patronymic_edit)

        # Номер читательского билета
        ticket_number_label = QLabel("Номер чит билета:")
        ticket_number_label.setStyleSheet(label_style)
        self.ticket_number_edit = ValidatedLineEdit(self.controller, self.reader['ticket_number'])
        layout.addRow(ticket_number_label, self.ticket_number_edit)

        # дата регистрации
        registration_date_label = QLabel("Дата регистрации:")
        registration_date_label.setStyleSheet(label_style)

        self.registration_date_edit = QDateEdit()
        self.registration_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.registration_date_edit.setCalendarPopup(True)

        # Устанавливаем значение из reader (строка или date)
        reg_date = self.reader['registration_date']
        if hasattr(reg_date, 'strftime'):
            reg_date_str = reg_date.strftime("%Y-%m-%d")
        else:
            reg_date_str = str(reg_date)
        self.registration_date_edit.setDate(QDate.fromString(reg_date_str, "yyyy-MM-dd"))

        layout.addRow(registration_date_label, self.registration_date_edit)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)

        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        """Валидация введенных данных и закрытие диалога с принятием."""
        # Проверка заполнения обязательных полей
        if not self.last_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите фамилию")
            return

        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя")
            return

        # Если все проверки пройдены, принимаем диалог
        self.accept()

class EditIssueDialog(QDialog):
    """
    Диалог редактирования данных заказа (выдачи книги).
    Позволяет изменить книгу, читателя, дату выдачи и дату возврата.
    """
    def __init__(self, controller, issue, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.issue = issue

        self.setWindowTitle("Редактировать данные заказа")
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = "color: #333333; font-weight: bold;"

        # Получаем список книг и читателей
        self.books = self.controller.get_all_books()
        self.readers = self.controller.get_all_readers()

        # Книга (выбор из существующих)
        book_id_label = QLabel("Книга:")
        book_id_label.setStyleSheet(label_style)
        self.book_id_combo = QComboBox()
        for book in self.books:
            self.book_id_combo.addItem(f"{book['book_id']} — {book['title']}", book['book_id'])
        # Установить текущий выбранный book_id
        index = self.book_id_combo.findData(self.issue['book_id'])
        if index >= 0:
            self.book_id_combo.setCurrentIndex(index)
        layout.addRow(book_id_label, self.book_id_combo)

        # Читатель (выбор из существующих)
        reader_id_label = QLabel("Читатель:")
        reader_id_label.setStyleSheet(label_style)
        self.reader_id_combo = QComboBox()
        for reader in self.readers:
            self.reader_id_combo.addItem(f"{reader['reader_id']} — {reader['last_name']} {reader['first_name']}", reader['reader_id'])
        index = self.reader_id_combo.findData(self.issue['reader_id'])
        if index >= 0:
            self.reader_id_combo.setCurrentIndex(index)
        layout.addRow(reader_id_label, self.reader_id_combo)

        # Дата выдачи
        issue_date_label = QLabel("Дата выдачи:")
        issue_date_label.setStyleSheet(label_style)
        self.issue_date_edit = QDateEdit()
        self.issue_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.issue_date_edit.setCalendarPopup(True)
        issue_date = self.issue['issue_date']
        if hasattr(issue_date, 'strftime'):
            issue_date_str = issue_date.strftime("%Y-%m-%d")
        else:
            issue_date_str = str(issue_date)
        self.issue_date_edit.setDate(QDate.fromString(issue_date_str, "yyyy-MM-dd"))
        layout.addRow(issue_date_label, self.issue_date_edit)

        # Дата возврата (может быть пустой)
        return_date_label = QLabel("Дата возврата:")
        return_date_label.setStyleSheet(label_style)
        self.return_date_edit = QDateEdit()
        self.return_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.return_date_edit.setCalendarPopup(True)
        return_date = self.issue['return_date']
        if return_date:
            if hasattr(return_date, 'strftime'):
                return_date_str = return_date.strftime("%Y-%m-%d")
            else:
                return_date_str = str(return_date)
            self.return_date_edit.setDate(QDate.fromString(return_date_str, "yyyy-MM-dd"))
        layout.addRow(return_date_label, self.return_date_edit)

        # Кнопки действий
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        # Проверка выбранных значений
        book_id = self.book_id_combo.currentData()
        reader_id = self.reader_id_combo.currentData()
        if book_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу")
            return
        if reader_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите читателя")
            return

        # Проверка корректности дат
        issue_date = self.issue_date_edit.date().toString("yyyy-MM-dd")
        return_date = self.return_date_edit.date().toString("yyyy-MM-dd")

        # Можно добавить дополнительные проверки на пустую дату возврата, если нужно

        self.accept()

class EditBookAuthorDialog(QDialog):
    """
    Диалог редактирования связи книга–автор.
    Позволяет изменить книгу и автора для существующей связи.
    """
    def __init__(self, controller, link, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.link = link  # link должен содержать 'book_id' и 'author_id'

        self.setWindowTitle("Редактировать связь книга–автор")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = "color: #333333; font-weight: bold;"

        # Получаем список книг и авторов
        self.books = self.controller.get_all_books()
        self.authors = self.controller.get_all_authors()

        # Книга (выбор из существующих)
        book_id_label = QLabel("Книга:")
        book_id_label.setStyleSheet(label_style)
        self.book_id_combo = QComboBox()
        for book in self.books:
            self.book_id_combo.addItem(f"{book['book_id']} — {book['title']}", book['book_id'])
        # Установить текущий выбранный book_id
        index = self.book_id_combo.findData(self.link['book_id'])
        if index >= 0:
            self.book_id_combo.setCurrentIndex(index)
        layout.addRow(book_id_label, self.book_id_combo)

        # Автор (выбор из существующих)
        author_id_label = QLabel("Автор:")
        author_id_label.setStyleSheet(label_style)
        self.author_id_combo = QComboBox()
        for author in self.authors:
            self.author_id_combo.addItem(f"{author['author_id']} — {author['last_name']} {author['first_name']}", author['author_id'])
        index = self.author_id_combo.findData(self.link['author_id'])
        if index >= 0:
            self.author_id_combo.setCurrentIndex(index)
        layout.addRow(author_id_label, self.author_id_combo)

        # Кнопки действий
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        # Проверка выбранных значений
        book_id = self.book_id_combo.currentData()
        author_id = self.author_id_combo.currentData()
        if book_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу")
            return
        if author_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите автора")
            return

        self.accept()

class ReadersDialog(QDialog):
    """
    Диалог управления читателями.
    Позволяет просматривать, добавлять, редактировать и удалять читателей
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.all_readers = controller.get_all_readers()

        self.setWindowTitle("Читатели")
        self.setMinimumSize(800, 600)

        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса диалога."""
        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("<h2>Читатели</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)



        # Таблица читателей
        self.readers_table = QTableWidget()
        self.readers_table.setColumnCount(6)
        self.readers_table.setHorizontalHeaderLabels(
            ["ID", "Фамилия", "Имя", "Отчество", "Номер чит билета", "Дата регистрации"])
        self.readers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.readers_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Заполнение таблицы данными
        self.update_readers_table()

        # Включение сортировки и обработки двойного клика
        self.readers_table.setSortingEnabled(True)
        self.readers_table.cellDoubleClicked.connect(self.edit_reader)

        layout.addWidget(self.readers_table)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        add_reader_btn = QPushButton("Добавить читателя")
        add_reader_btn.clicked.connect(self.add_reader)
        buttons_layout.addWidget(add_reader_btn)

        delete_reader_btn = QPushButton("Удалить читателя")
        delete_reader_btn.clicked.connect(self.delete_reader)
        buttons_layout.addWidget(delete_reader_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def update_readers_table(self):
        """Обновление содержимого таблицы читателей"""
        # Получение актуального списка читателей
        self.all_readers = self.controller.get_all_readers()
        self.readers_table.setRowCount(len(self.all_readers))

        # Временно отключаем сортировку для заполнения таблицы
        self.readers_table.setSortingEnabled(False)



        # Заполнение таблицы данными
        for i, reader in enumerate(self.all_readers):
            id_reader_item = NumericTableItem(str(reader['reader_id']), reader['reader_id'])
            last_name_item = QTableWidgetItem(reader['last_name'])
            first_name_item = QTableWidgetItem(reader['first_name'])
            patronymic_item = QTableWidgetItem(reader['patronymic'])
            ticket_number_item = NumericTableItem(str(reader['ticket_number']), reader['ticket_number'])
            registration_date_item = NumericTableItem(reader['registration_date'].strftime('%Y-%m-%d'), reader['registration_date'])


            self.readers_table.setItem(i, 0, id_reader_item)
            self.readers_table.setItem(i, 1, last_name_item)
            self.readers_table.setItem(i, 2, first_name_item)
            self.readers_table.setItem(i, 3, patronymic_item)
            self.readers_table.setItem(i, 4, ticket_number_item)
            self.readers_table.setItem(i, 5, registration_date_item)

        # Включаем сортировку обратно
        self.readers_table.setSortingEnabled(True)

    def add_reader(self):
        """Открытие диалога добавления нового читателя"""
        dialog = AddReaderDialog(self.controller, self)
        if dialog.exec():
            # Получаем данные из диалога
            last_name = dialog.last_name_edit.text().strip()
            first_name = dialog.first_name_edit.text().strip()
            patronymic = dialog.patronymic_edit.text().strip()
            ticket_number = dialog.ticket_number_edit.text().strip()
            registration_date = dialog.registration_date_edit.text().strip()

            # Добавление читателя в БД
            reader_id = self.controller.add_new_reader(
                last_name, first_name, patronymic, ticket_number, registration_date
            )

            if reader_id:
                self.update_readers_table()
                QMessageBox.information(self, "Успех", "Читатель успешно добавлен")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить читателя")

    def edit_reader(self, row, column):
        """Открытие диалога редактирования читателя"""
        # Получение ID читателя из таблицы
        reader_id = int(self.readers_table.item(row, 0).text())
        reader = next((a for a in self.all_readers if a['reader_id'] == reader_id), None)

        if not reader:
            return

        # Открытие диалога редактирования
        dialog = EditReaderDialog(self.controller, reader, self)
        if dialog.exec():
            # Если диалог был принят, получаем данные и обновляем читателя
            last_name = dialog.last_name_edit.text().strip()
            first_name = dialog.first_name_edit.text().strip()
            patronymic = dialog.patronymic_edit.text().strip()
            ticket_number = dialog.ticket_number_edit.text().strip()
            registration_date = dialog.registration_date_edit.text().strip()

            # Обновление читателя в БД
            success, message = self.controller.update_reader(
                reader_id, last_name, first_name, patronymic, ticket_number, registration_date
            )
            if success:
                # Обновление таблицы при успешном обновлении
                self.update_readers_table()
                QMessageBox.information(self, "Успех", "Читатель успешно обновлен")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить итателя: {message}")

    def delete_reader(self):
        """Удаление выбранного читателя"""
        # Проверка наличия выбранных строк
        selected_rows = self.readers_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите читателя для удаления")
            return

        # Получение ID читателя
        row = selected_rows[0].row()
        reader_id = int(self.readers_table.item(row, 0).text())

        # Запрос подтверждения
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить этого читателя?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Удаление читателя из БД
            success, message = self.controller.delete_reader_by_id(reader_id)

            if success:
                # Обновление таблицы при успешном удалении
                self.update_readers_table()
                QMessageBox.information(self, "Успех", "Читатель успешно удален")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить читателя: {message}")

class BookAuthorsDialog(QDialog):
    """
    Диалог управления связями автор–книга.
    Позволяет просматривать, добавлять, редактировать и удалять связи.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.all_links = controller.get_all_book_authors()  # список связей

        self.setWindowTitle("Связи автор–книга")
        self.setMinimumSize(800, 600)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("<h2>Автор–Книга</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Таблица связей
        self.links_table = QTableWidget()
        self.links_table.setColumnCount(3)
        self.links_table.setHorizontalHeaderLabels(
            ["ID связи", "ID книги", "ID автора"])
        self.links_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.links_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Заполнение таблицы данными
        self.update_links_table()

        # Включение сортировки и обработки двойного клика
        self.links_table.setSortingEnabled(True)
        self.links_table.cellDoubleClicked.connect(self.edit_link)

        layout.addWidget(self.links_table)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        add_link_btn = QPushButton("Добавить связь")
        add_link_btn.clicked.connect(self.add_link)
        buttons_layout.addWidget(add_link_btn)

        delete_link_btn = QPushButton("Удалить связь")
        delete_link_btn.clicked.connect(self.delete_link)
        buttons_layout.addWidget(delete_link_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def update_links_table(self):
        """Обновление содержимого таблицы связей"""
        self.all_links = self.controller.get_all_book_authors()
        self.links_table.setRowCount(len(self.all_links))
        self.links_table.setSortingEnabled(False)

        for i, link in enumerate(self.all_links):

            book_id_item = NumericTableItem(str(link['book_id']), link['book_id'])
            author_id_item = NumericTableItem(str(link['author_id']), link['author_id'])
            id_item = QTableWidgetItem(f"{link['book_id']}-{link['author_id']}")
            self.links_table.setItem(i, 0, id_item)
            self.links_table.setItem(i, 1, book_id_item)
            self.links_table.setItem(i, 2, author_id_item)

        self.links_table.setSortingEnabled(True)

    def add_link(self):
        """Открытие диалога добавления новой связи"""
        dialog = AddBookAuthorDialog(self.controller, self)
        if dialog.exec():
            book_id = int(dialog.book_id_combo.currentData())
            author_id = int(dialog.author_id_combo.currentData())
            link_id = self.controller.add_new_book_author(book_id, author_id)

            if link_id:
                self.update_links_table()
                QMessageBox.information(self, "Успех", "Связь успешно добавлена")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить связь")

    def edit_link(self, row, column):
        """Открытие диалога редактирования связи"""
        # Получаем строку вида "2-2"
        book_id_str, author_id_str = self.links_table.item(row, 0).text().split('-')
        book_id = int(book_id_str)
        author_id = int(author_id_str)

        # Ищем нужную связь
        link = next(
            (a for a in self.all_links if a['book_id'] == book_id and a['author_id'] == author_id),
            None
        )

        if not link:
            return

        dialog = EditBookAuthorDialog(self.controller, link, self)
        if dialog.exec():
            new_book_id = int(dialog.book_id_combo.currentData())
            new_author_id = int(dialog.author_id_combo.currentData())

            success, message = self.controller.update_book_author(book_id, author_id, new_book_id, new_author_id)
            if success:
                self.update_links_table()
                QMessageBox.information(self, "Успех", "Связь успешно обновлена")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить связь: {message}")

    def delete_link(self):
        """Удаление выбранной связи"""
        selected_rows = self.links_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите связь для удаления")
            return

        row = selected_rows[0].row()
        key_text = self.links_table.item(row, 0).text()
        book_id_str, author_id_str = key_text.split('-')
        book_id = int(book_id_str)
        author_id = int(author_id_str)

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить эту связь?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            success, message = self.controller.delete_book_author_by_id(book_id, author_id)
            if success:
                self.update_links_table()
                QMessageBox.information(self, "Успех", "Связь успешно удалена")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить связь: {message}")

class IssuesDialog(QDialog):
    """
    Диалог управления заказами (выдачами книг).
    Позволяет просматривать, добавлять, редактировать и удалять заказы.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.all_issues = controller.get_all_issues()

        self.setWindowTitle("Заказы (выдачи книг)")
        self.setMinimumSize(800, 600)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("<h2>Заказы</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Таблица заказов
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(5)
        self.issues_table.setHorizontalHeaderLabels(
            ["ID заказа", "ID книги", "ID читателя", "Дата выдачи", "Дата возврата"])
        self.issues_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.issues_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Заполнение таблицы данными
        self.update_issues_table()

        # Включение сортировки и обработки двойного клика
        self.issues_table.setSortingEnabled(True)
        self.issues_table.cellDoubleClicked.connect(self.edit_issue)

        layout.addWidget(self.issues_table)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        add_issue_btn = QPushButton("Добавить заказ")
        add_issue_btn.clicked.connect(self.add_issue)
        buttons_layout.addWidget(add_issue_btn)

        delete_issue_btn = QPushButton("Удалить заказ")
        delete_issue_btn.clicked.connect(self.delete_issue)
        buttons_layout.addWidget(delete_issue_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def update_issues_table(self):
        """Обновление содержимого таблицы заказов"""
        self.all_issues = self.controller.get_all_issues()
        self.issues_table.setRowCount(len(self.all_issues))
        self.issues_table.setSortingEnabled(False)

        for i, issue in enumerate(self.all_issues):
            id_issue_item = NumericTableItem(str(issue['issue_id']), issue['issue_id'])
            book_id_item = NumericTableItem(str(issue['book_id']), issue['book_id'])
            reader_id_item = NumericTableItem(str(issue['reader_id']), issue['reader_id'])
            issue_date_item = QTableWidgetItem(issue['issue_date'].strftime('%Y-%m-%d') if issue['issue_date'] else "")
            return_date_item = QTableWidgetItem(issue['return_date'].strftime('%Y-%m-%d') if issue['return_date'] else "")

            self.issues_table.setItem(i, 0, id_issue_item)
            self.issues_table.setItem(i, 1, book_id_item)
            self.issues_table.setItem(i, 2, reader_id_item)
            self.issues_table.setItem(i, 3, issue_date_item)
            self.issues_table.setItem(i, 4, return_date_item)

        self.issues_table.setSortingEnabled(True)

    def add_issue(self):
        """Открытие диалога добавления нового заказа"""
        dialog = AddIssueDialog(self.controller, self)
        if dialog.exec():
            book_id = int(dialog.book_id_combo.currentData())
            reader_id = int(dialog.reader_id_combo.currentData())
            issue_date = dialog.issue_date_edit.text().strip()
            return_date = dialog.return_date_edit.text().strip() or None
            issue_id = self.controller.add_new_issue(
                book_id, reader_id, issue_date, return_date
            )

            if issue_id:
                self.update_issues_table()
                QMessageBox.information(self, "Успех", "Заказ успешно добавлен")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить заказ")

    def edit_issue(self, row, column):
        """Открытие диалога редактирования заказа"""
        issue_id = int(self.issues_table.item(row, 0).text())
        issue = next((a for a in self.all_issues if a['issue_id'] == issue_id), None)

        if not issue:
            return

        dialog = EditIssueDialog(self.controller, issue, self)
        if dialog.exec():
            book_id = int(dialog.book_id_combo.currentData())
            reader_id = int(dialog.reader_id_combo.currentData())
            issue_date = dialog.issue_date_edit.text().strip()
            return_date = dialog.return_date_edit.text().strip() or None

            success, message = self.controller.update_issue(
                issue_id, book_id, reader_id, issue_date, return_date
            )
            if success:
                self.update_issues_table()
                QMessageBox.information(self, "Успех", "Заказ успешно обновлен")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить заказ: {message}")

    def delete_issue(self):
        """Удаление выбранного заказа"""
        selected_rows = self.issues_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ для удаления")
            return

        row = selected_rows[0].row()
        issue_id = int(self.issues_table.item(row, 0).text())

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить этот заказ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            success, message = self.controller.delete_issue_by_id(issue_id)
            if success:
                self.update_issues_table()
                QMessageBox.information(self, "Успех", "Заказ успешно удален")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить заказ: {message}")

class AddIssueDialog(QDialog):
    """
    Диалог добавления нового заказа (выдачи книги).
    Позволяет выбрать существующий ID книги и читателя, дату выдачи и дату возврата.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Добавить заказ")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = "color: #333333; font-weight: bold;"

        # Получаем список книг и читателей
        self.books = self.controller.get_all_books()    # список словарей книг
        self.readers = self.controller.get_all_readers() # список словарей читателей

        # ID книги (выбор из существующих)
        book_id_label = QLabel("ID книги:")
        book_id_label.setStyleSheet(label_style)
        self.book_id_combo = QComboBox()
        for book in self.books:
            # Можно выводить: "ID - Название"
            self.book_id_combo.addItem(f"{book['book_id']} — {book['title']}", book['book_id'])
        layout.addRow(book_id_label, self.book_id_combo)

        # ID читателя (выбор из существующих)
        reader_id_label = QLabel("ID читателя:")
        reader_id_label.setStyleSheet(label_style)
        self.reader_id_combo = QComboBox()
        for reader in self.readers:
            # Можно выводить: "ID - Фамилия Имя"
            self.reader_id_combo.addItem(f"{reader['reader_id']} — {reader['last_name']} {reader['first_name']}", reader['reader_id'])
        layout.addRow(reader_id_label, self.reader_id_combo)

        # Дата выдачи (по умолчанию сегодня, можно изменить)
        issue_date_label = QLabel("Дата выдачи (ГГГГ-ММ-ДД):")
        issue_date_label.setStyleSheet(label_style)
        self.issue_date_edit = QLineEdit()
        from datetime import date
        self.issue_date_edit.setText(str(date.today()))
        layout.addRow(issue_date_label, self.issue_date_edit)

        # Дата возврата (может быть пустой, если книга не возвращена)
        return_date_label = QLabel("Дата возврата (ГГГГ-ММ-ДД, можно оставить пустым):")
        return_date_label.setStyleSheet(label_style)
        self.return_date_edit = QLineEdit()
        layout.addRow(return_date_label, self.return_date_edit)

        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        # Получаем выбранные ID
        book_id = self.book_id_combo.currentData()
        reader_id = self.reader_id_combo.currentData()

        if book_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу")
            return
        if reader_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите читателя")
            return

        # Проверка корректности даты выдачи
        issue_date_str = self.issue_date_edit.text().strip()
        from datetime import datetime
        try:
            parsed_issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите дату выдачи в формате ГГГГ-ММ-ДД (например, 2024-09-29)")
            return

        # Проверка корректности даты возврата (если не пусто)
        return_date_str = self.return_date_edit.text().strip()
        if return_date_str:
            try:
                parsed_return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите дату возврата в формате ГГГГ-ММ-ДД (или оставьте пустым)")
                return

        self.accept()

class AddBookAuthorDialog(QDialog):
    """
    Диалог добавления новой связи книга–автор.
    Позволяет выбрать существующую книгу и автора.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Добавить связь книга–автор")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = "color: #333333; font-weight: bold;"

        # Получаем список книг и авторов
        self.books = self.controller.get_all_books()    # список словарей книг
        self.authors = self.controller.get_all_authors() # список словарей авторов

        # Книга (выбор из существующих)
        book_id_label = QLabel("Книга:")
        book_id_label.setStyleSheet(label_style)
        self.book_id_combo = QComboBox()
        for book in self.books:
            self.book_id_combo.addItem(f"{book['book_id']} — {book['title']}", book['book_id'])
        layout.addRow(book_id_label, self.book_id_combo)

        # Автор (выбор из существующих)
        author_id_label = QLabel("Автор:")
        author_id_label.setStyleSheet(label_style)
        self.author_id_combo = QComboBox()
        for author in self.authors:
            self.author_id_combo.addItem(f"{author['author_id']} — {author['last_name']} {author['first_name']}", author['author_id'])
        layout.addRow(author_id_label, self.author_id_combo)

        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        # Получаем выбранные ID
        book_id = self.book_id_combo.currentData()
        author_id = self.author_id_combo.currentData()

        if book_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу")
            return
        if author_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите автора")
            return

        self.accept()

class AddReaderDialog(QDialog):
    """
    Диалог добавления нового читателя.
    Позволяет ввести ФИО, номер читательского билета и дату регистрации.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Добавить читателя")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        label_style = "color: #333333; font-weight: bold;"

        # Фамилия
        last_name_label = QLabel("Фамилия:")
        last_name_label.setStyleSheet(label_style)
        self.last_name_edit = ValidatedLineEdit(self.controller)
        layout.addRow(last_name_label, self.last_name_edit)

        # Имя
        first_name_label = QLabel("Имя:")
        first_name_label.setStyleSheet(label_style)
        self.first_name_edit = ValidatedLineEdit(self.controller)
        layout.addRow(first_name_label, self.first_name_edit)

        # Отчество
        patronymic_label = QLabel("Отчество:")
        patronymic_label.setStyleSheet(label_style)
        self.patronymic_edit = ValidatedLineEdit(self.controller)
        layout.addRow(patronymic_label, self.patronymic_edit)

        # Номер читательского билета
        ticket_number_label = QLabel("Номер чит билета:")
        ticket_number_label.setStyleSheet(label_style)
        self.ticket_number_edit = ValidatedLineEdit(self.controller)
        layout.addRow(ticket_number_label, self.ticket_number_edit)

        # Дата регистрации (по умолчанию сегодня, можно изменить)
        registration_date_label = QLabel("Дата регистрации (ГГГГ-ММ-ДД):")
        registration_date_label.setStyleSheet(label_style)
        self.registration_date_edit = QLineEdit()
        from datetime import date
        self.registration_date_edit.setText(str(date.today()))
        layout.addRow(registration_date_label, self.registration_date_edit)

        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(save_btn)
        layout.addRow("", buttons_layout)

    def validate_and_accept(self):
        if not self.last_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите фамилию")
            return
        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя")
            return
        if not self.ticket_number_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите номер читательского билета")
            return

        # Проверка корректности даты
        date_str = self.registration_date_edit.text().strip()
        from datetime import datetime
        try:
            # Попытка распарсить дату
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите дату в формате ГГГГ-ММ-ДД (например, 2024-09-29)")
            return

        self.accept()
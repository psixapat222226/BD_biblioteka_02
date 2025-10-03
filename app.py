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


from NumericTableItem import NumericTableItem
from authors import AuthorsDialog
from books import BooksDialog
from readers import ReadersDialog
from issues import IssuesDialog
from bookauthors import BookAuthorsDialog
from controller import Controller
from logger import Logger


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
        self.controller = Controller()
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
        self.dark_theme_enabled=False

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
        
        # Кнопка переключения темы - ДОБАВЬТЕ ЭТУ КНОПКУ
        self.theme_btn = QPushButton("Темная тема")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        bottom_btn_layout.addWidget(self.theme_btn)

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
    
    def apply_dark_theme(self):
        #Применение темной темы
        dark_style = """
        QMainWindow, QDialog {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QPushButton {
            background-color: #495057;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #6c757d;
        }
        QPushButton:pressed {
            background-color: #5a6268;
        }
        QLabel {
            color: #ffffff;
        }
        QTableWidget {
            background-color: #3c3f41;
            color: #ffffff;
            border: 1px solid #555555;
            gridline-color: #555555;
        }
        QTableWidget::item:selected {
            background-color: #2e6f40;
            color: #ffffff;
        }
        QHeaderView::section {
            background-color: #495057;
            color: #ffffff;
            padding: 4px;
            border: 1px solid #555555;
            font-weight: bold;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #3c3f41;
        }
        QTabBar::tab {
            background-color: #495057;
            color: #ffffff;
            padding: 8px 12px;
            border: 1px solid #555555;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #3c3f41;
            font-weight: bold;
        }
        QComboBox {
            background-color: #495057;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px;
            min-height: 25px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #555555;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        QComboBox::down-arrow {
            image: none;
            width: 10px;
            height: 10px;
            background: #28a745;
            border-radius: 5px;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #555555;
            border-radius: 4px;
            background-color: #495057;
            color: #ffffff;
            selection-background-color: #2e6f40;
            selection-color: #ffffff;
            padding: 4px;
        }
        QLineEdit {
            background-color: #495057;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 4px;
            min-width: 120px;
        }
        QTextEdit {
            background-color: #495057;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 2px;
        }
        QSpinBox {
            background-color: #495057;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 1px 1px 1px 4px;
            min-width: 80px;
            max-height: 22px;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #6c757d;
            width: 16px;
            border: none;
            border-left: 1px solid #555555;
        }
        QSpinBox::up-button {
            border-top-right-radius: 3px;
            border-bottom: 1px solid #555555;
        }
        QSpinBox::down-button {
            border-bottom-right-radius: 3px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #2e6f40;
        }
        QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
            background-color: #28a745;
        }
        QSpinBox::up-arrow, QSpinBox::down-arrow {
            width: 6px;
            height: 6px;
            background: #28a745;
        }
        QSpinBox:focus {
            border: 1px solid #28a745;
        }
        QMessageBox {
            background-color: #3c3f41;
            color: #ffffff;
        }
        QMessageBox QLabel {
            color: #ffffff;
        }
        QMessageBox QPushButton {
            background-color: #495057;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-weight: bold;
            min-width: 40px;
            min-height: 20px;
        }
        QMessageBox QPushButton:hover {
            background-color: #6c757d;
        }
        """
        self.setStyleSheet(dark_style)
        
        # Особые стили для элементов, которые требуют индивидуальной настройки
        self.log_display.setStyleSheet("background-color: #1e1e1e; color: #00ff00;")
        
        # Обновить заголовок
        title_label = self.central_widget.findChild(QLabel)
        if title_label:
            title_label.setStyleSheet("color: #28a745; margin: 10px;")
    
    def toggle_theme(self):
        #Переключение между светлой и темной темой
        self.dark_theme_enabled = not self.dark_theme_enabled
        
        if self.dark_theme_enabled:
            self.apply_dark_theme()
            self.logger.info(f"Тема изменена на темную")
            self.theme_btn.setText("Светлая тема")
        else:
            self.set_application_style()  # Вернуть стандартную тему
            self.logger.info(f"Тема изменена на светлую")
            self.theme_btn.setText("Темная тема")

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

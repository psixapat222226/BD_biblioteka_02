from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                              QHBoxLayout, QWidget, QDialog, QMessageBox, QComboBox,
                              QSpinBox, QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit,
                              QFormLayout, QMenu, QTabWidget, QScrollArea, QFrame, QHeaderView, QTextEdit,)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QFont, QIntValidator,QAction
from ui.dialogs.bookauthors import BookAuthorsDialog
from ui.dialogs.authors import AuthorsDialog
from ui.dialogs.readers import ReadersDialog
from ui.dialogs.books import BooksDialog
from ui.dialogs.issues import IssuesDialog
from core.logger import Logger
from ui.styles import (get_light_theme_style, get_dark_theme_style, get_log_display_style, get_title_style)
from core.enums import TableType

from ui.dialogs.searchable_authors import SearchableAuthorsDialog
from ui.dialogs.searchable_books import SearchableBooksDialog
from ui.dialogs.searchable_readers import SearchableReadersDialog
from ui.dialogs.searchable_issues import SearchableIssuesDialog
from ui.dialogs.searchable_bookauthors import SearchableBookAuthorsDialog

class MainWindow(QMainWindow):
    """
    Главное окно приложения "Библиотека".
    Содержит все основные функции управления библиотекой.
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.logger = Logger()
        self.dark_theme_enabled = False

        self.setWindowTitle("Библиотека")
        self.setMinimumSize(900, 600)
        # Инициализация интерфейса
        self.setup_ui()
        # Установка стилей для всего приложения
        self.set_application_style()
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
        title_label.setStyleSheet(get_log_display_style())
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
        self.log_display.setStyleSheet(get_log_display_style())
        log_layout.addWidget(self.log_display)
        self.data_tabs.addTab(log_tab, "Логи")
        self.data_tabs.setCurrentIndex(0)

        # Регистрация дисплея логов в логгере
        self.logger.set_main_window_log_display(self.log_display)

        # Кнопки управления внизу
        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addStretch()

        # Кнопка переключения темы
        self.theme_btn = QPushButton("Темная тема")
        self.theme_btn.clicked.connect(self.toggle_theme)
        bottom_btn_layout.addWidget(self.theme_btn)

        self.reset_db_btn = QPushButton("Обновить данные")
        self.reset_db_btn.clicked.connect(self.reset_database)
        bottom_btn_layout.addWidget(self.reset_db_btn)

        self.reset_schema_btn = QPushButton("Обновить схему")
        self.reset_schema_btn.clicked.connect(self.reset_schema)
        bottom_btn_layout.addWidget(self.reset_schema_btn)

        self.alter_table_btn = QPushButton("Управление структурой БД")
        self.alter_table_btn.clicked.connect(self.open_alter_table_dialog)
        bottom_btn_layout.addWidget(self.alter_table_btn)

        # Кнопка отключения от БД
        self.disconnect_btn = QPushButton("Отключиться от БД")
        self.disconnect_btn.setFixedWidth(160)
        self.disconnect_btn.clicked.connect(self.disconnect_from_db)
        bottom_btn_layout.addWidget(self.disconnect_btn)
        bottom_btn_layout.addStretch()
        main_layout.addLayout(bottom_btn_layout)

    def open_alter_table_dialog(self):
        """Открыть диалог управления структурой БД"""
        from ui.dialogs.alter_table_dialog import AlterTableDialog

        # Получаем подключение из controller (как это делается в других методах)
        if hasattr(self.controller, 'cursor') and self.controller.cursor:
            # Получаем connection из cursor
            db_connection = self.controller.cursor.connection
            dialog = AlterTableDialog(db_connection, self)
            dialog.exec()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка",
                                "Нет активного подключения к базе данных. Подключитесь к БД сначала.")

    def apply_dark_theme(self):
        # Применение темной темы
        self.setStyleSheet(get_dark_theme_style())

        # Особые стили для элементов, которые требуют индивидуальной настройки
        self.log_display.setStyleSheet(get_log_display_style("dark"))

        # Обновить заголовок
        title_label = self.central_widget.findChild(QLabel)
        if title_label:
            title_label.setStyleSheet(get_title_style("dark"))

    def toggle_theme(self):
        # Переключение между светлой и темной темой
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

        # Создаем единую кнопку "Таблицы" с выпадающим меню
        self.tables_menu = QMenu(self)

        authors_action = QAction("Авторы", self)
        authors_action.triggered.connect(lambda: self.show_table(TableType.AUTHORS))
        self.tables_menu.addAction(authors_action)

        books_action = QAction("Книги", self)
        books_action.triggered.connect(lambda: self.show_table(TableType.BOOKS))
        self.tables_menu.addAction(books_action)

        readers_action = QAction("Читатели", self)
        readers_action.triggered.connect(lambda: self.show_table(TableType.READERS))
        self.tables_menu.addAction(readers_action)

        issues_action = QAction("Заказы", self)
        issues_action.triggered.connect(lambda: self.show_table(TableType.ISSUES))
        self.tables_menu.addAction(issues_action)

        book_authors_action = QAction("Автор/книга", self)
        book_authors_action.triggered.connect(lambda: self.show_table(TableType.BOOK_AUTHORS))
        self.tables_menu.addAction(book_authors_action)

        # Новый пункт: динамический обозреватель
        table_viewer_action = QAction("Обозреватель таблиц (динамич.)", self)
        table_viewer_action.triggered.connect(self.show_table_viewer)
        self.tables_menu.addAction(table_viewer_action)

        self.tables_btn = QPushButton("Таблицы")
        self.tables_btn.setMenu(self.tables_menu)
        self.tables_btn.setStyleSheet("""
            QPushButton::menu-indicator { 
                image: none; 
                width: 0px; 
                height: 0px;
            }
        """)

        buttons_layout.addWidget(self.tables_btn)

        self.join_btn = QPushButton("JOIN")
        self.join_btn.clicked.connect(self.show_join_wizard)
        buttons_layout.addWidget(self.join_btn)

        self.request_builder_btn = QPushButton("SELECT")
        self.request_builder_btn.clicked.connect(self.show_request_builder)
        buttons_layout.addWidget(self.request_builder_btn)

        main_layout.addLayout(buttons_layout)

    def show_table_viewer(self):
        """Открывает динамический обозреватель таблиц."""
        from ui.dialogs.table_viewer import TableViewerDialog
        dialog = TableViewerDialog(self.controller, self)
        dialog.exec()
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
        self.setStyleSheet(get_light_theme_style())
        self.log_display.setStyleSheet(get_log_display_style("light"))

        # Обновить заголовок
        title_label = self.central_widget.findChild(QLabel)
        if title_label:
            title_label.setStyleSheet(get_title_style("light"))

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

    def show_table(self, table_type):
        """Открывает диалог с выбранной таблицей."""
        if table_type == TableType.AUTHORS:
            dialog = SearchableAuthorsDialog(self.controller, self)
        elif table_type == TableType.BOOKS:
            dialog = SearchableBooksDialog(self.controller, self)
        elif table_type == TableType.READERS:
            dialog = SearchableReadersDialog(self.controller, self)
        elif table_type == TableType.ISSUES:
            dialog = SearchableIssuesDialog(self.controller, self)
        elif table_type == TableType.BOOK_AUTHORS:
            dialog = SearchableBookAuthorsDialog(self.controller, self)
        else:
            return

        dialog.exec()

    def show_join_wizard(self):
        """Открывает диалог мастера соединений."""
        from ..dialogs.join_dialog import JoinWizardDialog
        dialog = JoinWizardDialog(self.controller, self)
        dialog.exec()

    def show_request_builder(self):
        """Открытие диалога построителя запросов"""
        from ..dialogs.request_builder import RequestBuilderDialog
        dialog = RequestBuilderDialog(self.controller, self)
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
            self.controller.disconnect()
            #self.disconnect()
            QApplication.quit()

    def closeEvent(self, event):
        """Обработка события закрытия окна."""
        self.controller.disconnect()
        event.accept()

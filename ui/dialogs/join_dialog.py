from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                               QGroupBox, QRadioButton, QCheckBox, QLineEdit)
from PySide6.QtCore import Qt
from ui.styles import get_button_style, get_combobox_style, get_table_style, get_input_fields_style


class JoinWizardDialog(QDialog):
    """
    Мастер соединений для работы с JOIN запросами.
    Позволяет выбрать таблицы, поля и тип соединения.
    """

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Мастер соединений (JOIN)")
        self.setMinimumSize(900, 600)

        # Доступные таблицы и их поля
        self.tables_info = {
            "authors": ["author_id", "last_name", "first_name", "patronymic", "birth_year", "country"],
            "books": ["book_id", "title", "publication_year", "genre", "isbn", "available_copies"],
            "readers": ["reader_id", "last_name", "first_name", "patronymic", "ticket_number", "registration_date"],
            "issues": ["issue_id", "book_id", "reader_id", "issue_date", "return_date"],
            "book_authors": ["book_id", "author_id"]
        }

        self.setup_ui()
        self.selected_columns = []  # Хранит выбранные столбцы для запроса

    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        main_layout = QVBoxLayout(self)

        # Верхняя часть: выбор таблиц и настройка JOIN
        top_layout = QHBoxLayout()

        # Левая таблица
        left_table_group = QGroupBox("Первая таблица")
        left_table_layout = QVBoxLayout(left_table_group)

        self.left_table_combo = QComboBox()
        self.left_table_combo.addItems(self.tables_info.keys())
        self.left_table_combo.setStyleSheet(get_combobox_style())
        self.left_table_combo.currentTextChanged.connect(self.update_left_columns)
        left_table_layout.addWidget(QLabel("Выберите первую таблицу:"))
        left_table_layout.addWidget(self.left_table_combo)

        self.left_column_combo = QComboBox()
        self.left_column_combo.setStyleSheet(get_combobox_style())
        left_table_layout.addWidget(QLabel("Поле для соединения:"))
        left_table_layout.addWidget(self.left_column_combo)

        top_layout.addWidget(left_table_group)

        # Тип JOIN
        join_type_group = QGroupBox("Тип соединения")
        join_type_layout = QVBoxLayout(join_type_group)

        self.inner_join_radio = QRadioButton("INNER JOIN")
        self.inner_join_radio.setChecked(True)
        self.left_join_radio = QRadioButton("LEFT JOIN")
        self.right_join_radio = QRadioButton("RIGHT JOIN")
        self.full_join_radio = QRadioButton("FULL JOIN")

        join_type_layout.addWidget(self.inner_join_radio)
        join_type_layout.addWidget(self.left_join_radio)
        join_type_layout.addWidget(self.right_join_radio)
        join_type_layout.addWidget(self.full_join_radio)

        top_layout.addWidget(join_type_group)

        # Правая таблица
        right_table_group = QGroupBox("Вторая таблица")
        right_table_layout = QVBoxLayout(right_table_group)

        self.right_table_combo = QComboBox()
        self.right_table_combo.addItems(self.tables_info.keys())
        self.right_table_combo.setStyleSheet(get_combobox_style())
        self.right_table_combo.currentTextChanged.connect(self.update_right_columns)
        right_table_layout.addWidget(QLabel("Выберите вторую таблицу:"))
        right_table_layout.addWidget(self.right_table_combo)

        self.right_column_combo = QComboBox()
        self.right_column_combo.setStyleSheet(get_combobox_style())
        right_table_layout.addWidget(QLabel("Поле для соединения:"))
        right_table_layout.addWidget(self.right_column_combo)

        top_layout.addWidget(right_table_group)

        main_layout.addLayout(top_layout)

        # Выбор полей для отображения
        columns_group = QGroupBox("Выбор столбцов для отображения")
        columns_layout = QHBoxLayout(columns_group)

        # Левая таблица - выбор столбцов
        self.left_columns_group = QGroupBox("Столбцы первой таблицы")
        self.left_columns_layout = QVBoxLayout(self.left_columns_group)
        columns_layout.addWidget(self.left_columns_group)

        # Правая таблица - выбор столбцов
        self.right_columns_group = QGroupBox("Столбцы второй таблицы")
        self.right_columns_layout = QVBoxLayout(self.right_columns_group)
        columns_layout.addWidget(self.right_columns_group)

        main_layout.addWidget(columns_group)

        # Условия фильтрации (WHERE)
        filter_group = QGroupBox("Условия фильтрации (необязательно)")
        filter_layout = QHBoxLayout(filter_group)

        self.filter_column_combo = QComboBox()
        self.filter_column_combo.setStyleSheet(get_combobox_style())
        filter_layout.addWidget(QLabel("Поле:"))
        filter_layout.addWidget(self.filter_column_combo)

        self.filter_operator_combo = QComboBox()
        self.filter_operator_combo.addItems(
            ["=", ">", "<", ">=", "<=", "LIKE", "NOT LIKE", "IN", "NOT IN", "IS NULL", "IS NOT NULL"])
        self.filter_operator_combo.setStyleSheet(get_combobox_style())
        filter_layout.addWidget(QLabel("Оператор:"))
        filter_layout.addWidget(self.filter_operator_combo)

        self.filter_value_edit = QLineEdit()
        self.filter_value_edit.setStyleSheet(get_input_fields_style())
        filter_layout.addWidget(QLabel("Значение:"))
        filter_layout.addWidget(self.filter_value_edit)

        main_layout.addWidget(filter_group)

        # Результат запроса
        result_label = QLabel("Результат запроса:")
        main_layout.addWidget(result_label)

        self.result_table = QTableWidget()
        self.result_table.setStyleSheet(get_table_style())
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.result_table)

        # Кнопки внизу
        buttons_layout = QHBoxLayout()

        self.execute_btn = QPushButton("Выполнить запрос")
        self.execute_btn.clicked.connect(self.execute_query)
        self.execute_btn.setStyleSheet(get_button_style())
        buttons_layout.addWidget(self.execute_btn)

        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setStyleSheet(get_button_style())
        buttons_layout.addWidget(self.close_btn)

        main_layout.addLayout(buttons_layout)

        # Инициализация списков столбцов
        self.update_left_columns(self.left_table_combo.currentText())
        self.update_right_columns(self.right_table_combo.currentText())

    def update_left_columns(self, table_name):
        """Обновление списка столбцов левой таблицы."""
        self.left_column_combo.clear()
        self.clear_layout(self.left_columns_layout)

        if table_name in self.tables_info:
            columns = self.tables_info[table_name]
            self.left_column_combo.addItems(columns)

            # Создаем чекбоксы для выбора столбцов
            for column in columns:
                checkbox = QCheckBox(f"{table_name}.{column}")
                checkbox.setChecked(True)  # По умолчанию выбраны все
                self.left_columns_layout.addWidget(checkbox)

            # Обновляем список полей для фильтрации
            self.update_filter_columns()

    def update_right_columns(self, table_name):
        """Обновление списка столбцов правой таблицы."""
        self.right_column_combo.clear()
        self.clear_layout(self.right_columns_layout)

        if table_name in self.tables_info:
            columns = self.tables_info[table_name]
            self.right_column_combo.addItems(columns)

            # Создаем чекбоксы для выбора столбцов
            for column in columns:
                checkbox = QCheckBox(f"{table_name}.{column}")
                checkbox.setChecked(True)  # По умолчанию выбраны все
                self.right_columns_layout.addWidget(checkbox)

            # Обновляем список полей для фильтрации
            self.update_filter_columns()

    def update_filter_columns(self):
        """Обновление списка столбцов для фильтрации."""
        self.filter_column_combo.clear()

        left_table = self.left_table_combo.currentText()
        right_table = self.right_table_combo.currentText()

        if left_table in self.tables_info and right_table in self.tables_info:
            # Добавляем столбцы обеих таблиц с префиксами
            for column in self.tables_info[left_table]:
                self.filter_column_combo.addItem(f"{left_table}.{column}")

            for column in self.tables_info[right_table]:
                self.filter_column_combo.addItem(f"{right_table}.{column}")

    def get_selected_columns(self):
        """Получение выбранных столбцов из чекбоксов."""
        selected_columns = []

        # Левая таблица
        for i in range(self.left_columns_layout.count()):
            checkbox = self.left_columns_layout.itemAt(i).widget()
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                selected_columns.append(checkbox.text())

        # Правая таблица
        for i in range(self.right_columns_layout.count()):
            checkbox = self.right_columns_layout.itemAt(i).widget()
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                selected_columns.append(checkbox.text())

        return selected_columns

    def get_join_type(self):
        """Получение выбранного типа JOIN."""
        if self.inner_join_radio.isChecked():
            return "INNER JOIN"
        elif self.left_join_radio.isChecked():
            return "LEFT JOIN"
        elif self.right_join_radio.isChecked():
            return "RIGHT JOIN"
        elif self.full_join_radio.isChecked():
            return "FULL JOIN"
        return "INNER JOIN"  # По умолчанию

    def build_query(self):
        """Построение SQL запроса на основе выбранных параметров."""
        left_table = self.left_table_combo.currentText()
        right_table = self.right_table_combo.currentText()
        left_column = self.left_column_combo.currentText()
        right_column = self.right_column_combo.currentText()
        join_type = self.get_join_type()

        selected_columns = self.get_selected_columns()
        if not selected_columns:
            selected_columns = ["*"]  # Если ничего не выбрано, выбираем все

        # Начинаем составлять запрос
        query = f"SELECT {', '.join(selected_columns)} FROM {left_table} {join_type} {right_table} ON {left_table}.{left_column} = {right_table}.{right_column}"

        # Добавляем условие WHERE, если задано
        filter_column = self.filter_column_combo.currentText()
        filter_operator = self.filter_operator_combo.currentText()
        filter_value = self.filter_value_edit.text().strip()

        if filter_column and filter_value and filter_operator not in ["IS NULL", "IS NOT NULL"]:
            query += f" WHERE {filter_column} {filter_operator} "

            # В зависимости от оператора, обрабатываем значение
            if filter_operator == "LIKE" or filter_operator == "NOT LIKE":
                query += f"'%{filter_value}%'"
            elif filter_operator == "IN" or filter_operator == "NOT IN":
                values = [item.strip() for item in filter_value.split(",")]
                query += f"({', '.join([f'\'{value}\'' for value in values])})"
            else:
                query += f"'{filter_value}'"
        elif filter_column and (filter_operator == "IS NULL" or filter_operator == "IS NOT NULL"):
            query += f" WHERE {filter_column} {filter_operator}"

        return query

    def clear_layout(self, layout):
        """Очищает все виджеты из layout."""
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def execute_query(self):
        """Выполнение запроса и отображение результатов."""
        query = self.build_query()

        try:
            self.controller.cursor.execute(query)
            results = self.controller.cursor.fetchall()

            # Очищаем таблицу результатов
            self.result_table.clear()

            if results:
                # Настраиваем заголовки
                column_names = [desc[0] for desc in self.controller.cursor.description]
                self.result_table.setColumnCount(len(column_names))
                self.result_table.setHorizontalHeaderLabels(column_names)

                # Заполняем таблицу данными
                self.result_table.setRowCount(len(results))
                for i, row in enumerate(results):
                    for j, value in enumerate(row):
                        item = QTableWidgetItem(str(value) if value is not None else "")
                        self.result_table.setItem(i, j, item)

                # Включаем сортировку
                self.result_table.setSortingEnabled(True)

                QMessageBox.information(self, "Успех", f"Запрос успешно выполнен. Найдено записей: {len(results)}")
            else:
                self.result_table.setRowCount(0)
                QMessageBox.information(self, "Результат", "Запрос выполнен, но не найдено подходящих записей.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                               QGroupBox, QRadioButton, QCheckBox, QLineEdit)
from PySide6.QtCore import Qt
from ui.styles import get_button_style, get_combobox_style, get_table_style, get_input_fields_style,get_dark_theme_style,get_light_theme_style
import re


class JoinWizardDialog(QDialog):
    """
    Мастер соединений для работы с JOIN запросами.
    Позволяет выбрать таблицы, поля и тип соединения.
    """

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.parent=parent
        self.setWindowTitle("Мастер соединений (JOIN)")
        self.setMinimumSize(900, 600)

        # Больше не храним жестко столбцы — всё тянем из БД динамически
        self.setup_ui()
        self.selected_columns = []  # Хранит выбранные столбцы для запроса
    
    def apply_theme(self):
        """Применяет текущую тему ко всем элементам диалога."""
        if hasattr(self.parent, 'dark_theme_enabled') and self.parent.dark_theme_enabled:
            self.setStyleSheet(get_dark_theme_style())
        else:
            self.setStyleSheet(get_light_theme_style())

    def showEvent(self, event):
        """Обработчик события показа диалога."""
        super().showEvent(event)
        self.apply_theme()

    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        main_layout = QVBoxLayout(self)

        # Верхняя часть: выбор таблиц и настройка JOIN
        top_layout = QHBoxLayout()

        # Левая таблица
        left_table_group = QGroupBox("Первая таблица")
        left_table_layout = QVBoxLayout(left_table_group)

        self.left_table_combo = QComboBox()
        self.left_table_combo.currentTextChanged.connect(self.update_left_columns)
        left_table_layout.addWidget(QLabel("Выберите первую таблицу:"))
        left_table_layout.addWidget(self.left_table_combo)

        self.left_column_combo = QComboBox()
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
        self.right_table_combo.currentTextChanged.connect(self.update_right_columns)
        right_table_layout.addWidget(QLabel("Выберите вторую таблицу:"))
        right_table_layout.addWidget(self.right_table_combo)
        self.right_column_combo = QComboBox()
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
        filter_layout.addWidget(QLabel("Поле:"))
        filter_layout.addWidget(self.filter_column_combo)

        self.filter_operator_combo = QComboBox()
        self.filter_operator_combo.addItems(
            ["=", ">", "<", ">=", "<=", "LIKE", "NOT LIKE", "IN", "NOT IN", "IS NULL", "IS NOT NULL"])
        filter_layout.addWidget(QLabel("Оператор:"))
        filter_layout.addWidget(self.filter_operator_combo)

        self.filter_value_edit = QLineEdit()
        filter_layout.addWidget(QLabel("Значение:"))
        filter_layout.addWidget(self.filter_value_edit)

        main_layout.addWidget(filter_group)

        # Результат запроса
        result_label = QLabel("Результат запроса:")
        main_layout.addWidget(result_label)

        self.result_table = QTableWidget()
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.result_table)

        # Кнопки внизу
        buttons_layout = QHBoxLayout()

        self.execute_btn = QPushButton("Выполнить запрос")
        self.execute_btn.clicked.connect(self.execute_query)
        buttons_layout.addWidget(self.execute_btn)

        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_btn)

        main_layout.addLayout(buttons_layout)

        # Инициализация списков таблиц/столбцов
        self.reload_tables()

    def reload_tables(self):
        """Загружает список таблиц и заполняет комбобоксы."""
        tables = self.controller.get_tables() or []
        self.left_table_combo.clear()
        self.right_table_combo.clear()
        self.left_table_combo.addItems(tables)
        self.right_table_combo.addItems(tables)

        # Триггеры обновят столбцы
        if tables:
            self.update_left_columns(self.left_table_combo.currentText())
            self.update_right_columns(self.right_table_combo.currentText())

    def update_left_columns(self, table_name):
        """Обновление списка столбцов левой таблицы."""
        self.left_column_combo.clear()
        self.clear_layout(self.left_columns_layout)

        if table_name:
            columns = self.controller.get_table_columns(table_name) or []
            self.left_column_combo.addItems(columns)

            for column in columns:
                checkbox = QCheckBox(f"{table_name}.{column}")
                checkbox.setChecked(True)  # По умолчанию выбраны все
                self.left_columns_layout.addWidget(checkbox)

            self.update_filter_columns()

    def update_right_columns(self, table_name):
        """Обновление списка столбцов правой таблицы."""
        self.right_column_combo.clear()
        self.clear_layout(self.right_columns_layout)

        if table_name:
            columns = self.controller.get_table_columns(table_name) or []
            self.right_column_combo.addItems(columns)

            for column in columns:
                checkbox = QCheckBox(f"{table_name}.{column}")
                checkbox.setChecked(True)
                self.right_columns_layout.addWidget(checkbox)

            self.update_filter_columns()

    def update_filter_columns(self):
        """Обновление списка столбцов для фильтрации."""
        self.filter_column_combo.clear()

        left_table = self.left_table_combo.currentText()
        right_table = self.right_table_combo.currentText()

        if left_table:
            for column in self.controller.get_table_columns(left_table) or []:
                self.filter_column_combo.addItem(f"{left_table}.{column}")

        if right_table:
            for column in self.controller.get_table_columns(right_table) or []:
                self.filter_column_combo.addItem(f"{right_table}.{column}")

    def get_selected_columns(self):
        """Получение выбранных столбцов из чекбоксов."""
        selected_columns = []

        for i in range(self.left_columns_layout.count()):
            checkbox = self.left_columns_layout.itemAt(i).widget()
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                selected_columns.append(checkbox.text())

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
            selected_columns = ["*"]

        query = (
            f"SELECT {', '.join(selected_columns)} "
            f"FROM {left_table} {join_type} {right_table} "
            f"ON {left_table}.{left_column} = {right_table}.{right_column}"
        )

        filter_column = self.filter_column_combo.currentText()
        filter_operator = self.filter_operator_combo.currentText()
        filter_value = self.filter_value_edit.text().strip()

        def is_numeric(val: str) -> bool:
            return bool(re.fullmatch(r"-?\d+(\.\d+)?", val))

        if filter_column and filter_operator not in ["IS NULL", "IS NOT NULL"]:
            if not filter_value:
                return query

            query += f" WHERE {filter_column} {filter_operator} "

            if filter_operator in ("LIKE", "NOT LIKE"):
                query += f"'%{filter_value}%'"
            elif filter_operator in ("IN", "NOT IN"):
                values = [item.strip() for item in filter_value.split(",") if item.strip()]
                normalized = [v if is_numeric(v) else f"'{v}'" for v in values]
                query += f"({', '.join(normalized)})"
            else:
                if is_numeric(filter_value):
                    query += filter_value
                else:
                    query += f"'{filter_value}'"
        elif filter_column and filter_operator in ("IS NULL", "IS NOT NULL"):
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
            results = self.controller.execute_custom_request(query)

            self.result_table.clear()

            if results:
                column_names = list(results[0].keys())
                self.result_table.setColumnCount(len(column_names))
                self.result_table.setHorizontalHeaderLabels(column_names)

                self.result_table.setRowCount(len(results))
                for i, row in enumerate(results):
                    for j, col in enumerate(column_names):
                        val = row.get(col)
                        item = QTableWidgetItem("" if val is None else str(val))
                        self.result_table.setItem(i, j, item)

                self.result_table.setSortingEnabled(True)
                QMessageBox.information(self, "Успех", f"Запрос успешно выполнен. Найдено записей: {len(results)}")
            else:
                self.result_table.setRowCount(0)
                self.result_table.setColumnCount(0)
                QMessageBox.information(self, "Результат", "Запрос выполнен, но не найдено подходящих записей.")
        except Exception as e:
            # Снимаем состояние aborted на всякий случай
            try:
                if hasattr(self.controller, "connection") and self.controller.connection:
                    self.controller.connection.rollback()
            except Exception:
                pass
            QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса:\n{str(e)}")

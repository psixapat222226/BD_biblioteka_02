from PySide6.QtWidgets import (QDialog,QMessageBox,QScrollArea, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, 
                              QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                              QLabel, QFormLayout)
from PySide6.QtCore import Qt
from core.additional_classes import RequestBuilder

class RequestBuilderDialog(QDialog):
    """
    Построение сложных запросов к базе данных с визуальным интерфейсом
    """
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.request_builder = RequestBuilder()
        self.isMaximized=False
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.setWindowTitle("SELECT")
        self.setMinimumSize(1200, 800)
        
        # Выбор таблицы
        table_group = QGroupBox("Выбор таблицы")
        table_layout = QHBoxLayout(table_group)
        self.table_combo = QComboBox()
        self.table_combo.addItems(["authors", "books", "readers", "issues", "book_authors"])
        self.table_combo.currentTextChanged.connect(self.on_table_changed)
        table_layout.addWidget(QLabel("Таблица:"))
        table_layout.addWidget(self.table_combo)
        table_layout.addStretch()
        
        layout.addWidget(table_group)
        
        # Выбор столбцов
        columns_group = QGroupBox("Выбор столбцов")
        columns_layout = QVBoxLayout(columns_group)
        self.columns_layout = QVBoxLayout()
        columns_layout.addLayout(self.columns_layout)
        layout.addWidget(columns_group)
        
        # Условия WHERE
        where_group = QGroupBox("Условия фильтрации (WHERE)")
        where_layout = QFormLayout(where_group)
        self.where_condition = QLineEdit()
        self.where_condition.setPlaceholderText("например: publication_year > 2000")
        where_layout.addRow("Условие:", self.where_condition)
        layout.addWidget(where_group)
        
        # Сортировка ORDER BY
        order_group = QGroupBox("Сортировка (ORDER BY)")
        order_layout = QHBoxLayout(order_group)
        self.order_column = QComboBox()
        self.order_column.addItem("")
        self.order_direction = QComboBox()
        self.order_direction.addItems(["ASC", "DESC"])
        order_layout.addWidget(QLabel("Столбец:"))
        order_layout.addWidget(self.order_column)
        order_layout.addWidget(QLabel("Направление:"))
        order_layout.addWidget(self.order_direction)
        layout.addWidget(order_group)
        
        # Группировка и агрегатные функции
        group_group = QGroupBox("Группировка и агрегатные функции")
        group_layout = QFormLayout(group_group)
        self.group_column = QComboBox()
        self.group_column.addItem("")
        self.aggregate_function = QComboBox()
        self.aggregate_function.addItems(["", "COUNT", "SUM", "AVG", "MAX", "MIN"])
        self.having_condition = QLineEdit()
        group_layout.addRow("Группировать по:", self.group_column)
        group_layout.addRow("Агрегатная функция:", self.aggregate_function)
        group_layout.addRow("Условие HAVING:", self.having_condition)
        layout.addWidget(group_group)
        
        # Кнопки выполнения
        buttons_layout = QHBoxLayout()
        self.execute_btn = QPushButton("Выполнить запрос")
        self.execute_btn.clicked.connect(self.execute_request)
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.execute_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Результаты
        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)
        
        # Инициализация
        self.on_table_changed(self.table_combo.currentText())
    
    def on_table_changed(self, table_name):
        """Обновление доступных столбцов при смене таблицы"""
        # Очистка предыдущих чекбоксов
        for i in reversed(range(self.columns_layout.count())):
            widget = self.columns_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Получение столбцов для выбранной таблицы
        columns = self.controller.get_table_columns(table_name)
        for column in columns:
            checkbox = QCheckBox(column)
            checkbox.setChecked(True)
            self.columns_layout.addWidget(checkbox)
        
        current_order = self.order_column.currentText()
        current_group = self.group_column.currentText()
        self.order_column.clear()
        self.group_column.clear()
        self.order_column.addItem("")
        self.group_column.addItem("")
        
        # Добавляем столбцы
        self.order_column.addItems(columns)
        self.group_column.addItems(columns)
        
        # Восстанавливаем предыдущие значения, если они есть в новой таблице
        if current_order in columns:
            self.order_column.setCurrentText(current_order)
        if current_group in columns:
            self.group_column.setCurrentText(current_group)
    
    def execute_request(self):
        """Построение и выполнение SQL-запроса"""
        try:
            # Сбор выбранных столбцов
            selected_columns = []
            for i in range(self.columns_layout.count()):
                checkbox = self.columns_layout.itemAt(i).widget()
                if checkbox and checkbox.isChecked():
                    selected_columns.append(checkbox.text())
            
            if not selected_columns:
                selected_columns = ["*"]
            
            # Построение запроса
            self.request_builder.reset()
            
            group_column = self.group_column.currentText()
            
            # Обработка группировки
            if group_column:
                # Если есть группировка, добавляем агрегатную функцию если не указана
                if not self.aggregate_function.currentText():
                    self.request_builder.aggregate("COUNT", "*")
                
                # Для GROUP BY оставляем только столбец группировки
                final_columns = [group_column]
                self.request_builder.select(final_columns)
                
                self.request_builder.group_by(group_column)
                
                # Если выбрана агрегатная функция
                if self.aggregate_function.currentText():
                    if self.aggregate_function.currentText() == "COUNT":
                        aggregate_column = "*"
                    else:
                        numeric_columns = self.get_numeric_columns(self.table_combo.currentText())
                        if numeric_columns:
                            aggregate_column = numeric_columns[0]
                        else:
                            QMessageBox.warning(self, "Предупреждение", 
                                            f"Для функции {self.aggregate_function.currentText()} нужен числовой столбец.")
                            return
                    
                    self.request_builder.aggregate(
                        self.aggregate_function.currentText(),
                        aggregate_column
                    )
                
                if self.having_condition.text():
                    self.request_builder.having(self.having_condition.text())
                    
            else:
                # Без группировки используем все выбранные столбцы
                if selected_columns:
                    self.request_builder.select(selected_columns)
            
            self.request_builder.from_table(self.table_combo.currentText())
            
            if self.where_condition.text():
                self.request_builder.where(self.where_condition.text())
            
            # ORDER BY только если выбран столбец
            order_column = self.order_column.currentText()
            if order_column:
                # Проверяем конфликт GROUP BY и ORDER BY
                if group_column and order_column != group_column:
                    QMessageBox.information(self, "Информация", 
                                        f"Сортировка изменена с '{order_column}' на '{group_column}' из-за группировки")
                    self.request_builder.order_by(group_column, self.order_direction.currentText())
                else:
                    self.request_builder.order_by(order_column, self.order_direction.currentText())
            
            # Выполнение запроса
            sql = self.request_builder.build()
            self.controller.logger.info(f"Выполняется запрос: {sql}")
            results = self.controller.execute_custom_request(sql)
            
            # Отображение результатов
            self.display_results(results)
        
        except Exception as e:
            self.controller.logger.error(f"Ошибка выполнения запроса: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось выполнить запрос:\n{str(e)}")
    def get_numeric_columns(self, table_name):
        """Получение списка числовых столбцов таблицы через контроллер"""
        try:
            return self.controller.get_numeric_columns(table_name)
        except Exception as e:
            self.controller.logger.error(f"Ошибка получения числовых столбцов: {str(e)}")
            return []
            
    def display_results(self, results):
        """Отображение результатов в таблице"""
        if not results:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
            
        self.results_table.setRowCount(len(results))
        
        if results:
            # Получаем ключи из первого элемента как заголовки
            columns = list(results[0].keys())
            self.results_table.setColumnCount(len(columns))
            self.results_table.setHorizontalHeaderLabels(columns)
        
        # Данные
        for row_idx, row_data in enumerate(results):
            for col_idx, (key, value) in enumerate(row_data.items()):
                self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    def clear_form(self):
        """Очистка формы"""
        self.where_condition.clear()
        self.having_condition.clear()
        self.aggregate_function.setCurrentIndex(0)
        self.order_column.setCurrentIndex(0)
        self.group_column.setCurrentIndex(0)

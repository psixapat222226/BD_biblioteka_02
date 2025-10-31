from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QComboBox, QLineEdit, QTextEdit, QSpinBox,
                              QFormLayout, QGroupBox)
from PySide6.QtCore import Qt
from ..styles import get_form_label_style

class StringOperationsDialog(QDialog):
    def __init__(self, table_data, parent=None):
        super().__init__(parent)
        self.table_data = table_data
        self.setWindowTitle("Строковые операции")
        self.setMinimumSize(800, 800)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Общий стиль для QGroupBox
        group_style = """
        QGroupBox {
            border: 2px solid #666;
            border-radius: 5px;
            margin-top: 1em;
            padding-top: 10px;
        }
        QGroupBox::title {
            color: #666;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
            font-weight: bold;
        }
        """

        # Группа выбора данных
        data_group = QGroupBox("Выбор данных")
        data_group.setStyleSheet(group_style)
        data_layout = QFormLayout()
        
        self.column_combo = QComboBox()
        self.row_combo = QComboBox()
        
        # Заполняем комбобоксы данными из таблицы
        if self.table_data:
            # Получаем заголовки столбцов
            headers = [self.table_data['headers'][i] for i in range(len(self.table_data['headers']))]
            self.column_combo.addItems(headers)
            
            # Получаем номера строк
            row_numbers = [str(i+1) for i in range(len(self.table_data['rows']))]
            self.row_combo.addItems(row_numbers)

        data_layout.addRow("Столбец:", self.column_combo)
        data_layout.addRow("Строка:", self.row_combo)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        # Группа операций
        operations_group = QGroupBox("Операции")
        operations_group.setStyleSheet(group_style)
        operations_layout = QVBoxLayout()

        # Преобразование регистра
        case_layout = QHBoxLayout()
        upper_btn = QPushButton("UPPER")
        upper_btn.clicked.connect(self.upper_case)
        lower_btn = QPushButton("LOWER")
        lower_btn.clicked.connect(self.lower_case)
        case_layout.addWidget(upper_btn)
        case_layout.addWidget(lower_btn)
        operations_layout.addLayout(case_layout)

        # Извлечение подстроки
        substring_group = QGroupBox("SUBSTRING")
        substring_group.setStyleSheet(group_style)
        substring_layout = QHBoxLayout()
        self.start_spin = QSpinBox()
        self.start_spin.setMinimum(1)
        self.length_spin = QSpinBox()
        self.length_spin.setMinimum(1)
        substring_btn = QPushButton("Извлечь")
        substring_btn.clicked.connect(self.substring)
        substring_layout.addWidget(QLabel("Начало:"))
        substring_layout.addWidget(self.start_spin)
        substring_layout.addWidget(QLabel("Длина:"))
        substring_layout.addWidget(self.length_spin)
        substring_layout.addWidget(substring_btn)
        substring_group.setLayout(substring_layout)
        operations_layout.addWidget(substring_group)

        # Удаление пробелов
        trim_group = QGroupBox("Удаление пробелов")
        trim_group.setStyleSheet(group_style)
        trim_layout = QHBoxLayout()
        trim_btn = QPushButton("TRIM")
        trim_btn.clicked.connect(self.trim)
        ltrim_btn = QPushButton("LTRIM")
        ltrim_btn.clicked.connect(self.ltrim)
        rtrim_btn = QPushButton("RTRIM")
        rtrim_btn.clicked.connect(self.rtrim)
        trim_layout.addWidget(trim_btn)
        trim_layout.addWidget(ltrim_btn)
        trim_layout.addWidget(rtrim_btn)
        trim_group.setLayout(trim_layout)
        operations_layout.addWidget(trim_group)

        # Дополнение строк
        pad_group = QGroupBox("Дополнение строк")
        pad_group.setStyleSheet(group_style)
        pad_layout = QHBoxLayout()
        self.pad_char = QLineEdit()
        self.pad_char.setMaxLength(1)
        self.pad_char.setPlaceholderText("Символ")
        self.pad_length = QSpinBox()
        self.pad_length.setMinimum(1)
        lpad_btn = QPushButton("LPAD")
        lpad_btn.clicked.connect(self.lpad)
        rpad_btn = QPushButton("RPAD")
        rpad_btn.clicked.connect(self.rpad)
        pad_layout.addWidget(QLabel("Символ:"))
        pad_layout.addWidget(self.pad_char)
        pad_layout.addWidget(QLabel("Длина:"))
        pad_layout.addWidget(self.pad_length)
        pad_layout.addWidget(lpad_btn)
        pad_layout.addWidget(rpad_btn)
        pad_group.setLayout(pad_layout)
        operations_layout.addWidget(pad_group)

        # Объединение строк
        concat_group = QGroupBox("Объединение строк")
        concat_group.setStyleSheet(group_style)
        concat_layout = QVBoxLayout()
        self.concat_text = QLineEdit()
        self.concat_text.setPlaceholderText("Введите текст для объединения")
        concat_btns = QHBoxLayout()
        concat_btn = QPushButton("CONCAT")
        concat_btn.clicked.connect(self.concat)
        concat_op_btn = QPushButton("||")
        concat_op_btn.clicked.connect(self.concat_operator)
        concat_btns.addWidget(concat_btn)
        concat_btns.addWidget(concat_op_btn)
        concat_layout.addWidget(self.concat_text)
        concat_layout.addLayout(concat_btns)
        concat_group.setLayout(concat_layout)
        operations_layout.addWidget(concat_group)

        operations_group.setLayout(operations_layout)
        layout.addWidget(operations_group)

        # Результат
        result_group = QGroupBox("Результат")
        result_group.setStyleSheet(group_style)
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(100)  # Устанавливаем минимальную высоту для поля результата
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

    def get_selected_text(self):
        if not self.table_data:
            return ""
        row = int(self.row_combo.currentText()) - 1
        col = self.column_combo.currentIndex()
        return str(self.table_data['rows'][row][col])

    def upper_case(self):
        text = self.get_selected_text()
        self.result_text.setText(text.upper())

    def lower_case(self):
        text = self.get_selected_text()
        self.result_text.setText(text.lower())

    def substring(self):
        text = self.get_selected_text()
        start = self.start_spin.value() - 1
        length = self.length_spin.value()
        self.result_text.setText(text[start:start + length])

    def trim(self):
        text = self.get_selected_text()
        self.result_text.setText(text.strip())

    def ltrim(self):
        text = self.get_selected_text()
        self.result_text.setText(text.lstrip())

    def rtrim(self):
        text = self.get_selected_text()
        self.result_text.setText(text.rstrip())

    def lpad(self):
        text = self.get_selected_text()
        char = self.pad_char.text() or ' '
        length = self.pad_length.value()
        self.result_text.setText(text.rjust(length, char[0]))

    def rpad(self):
        text = self.get_selected_text()
        char = self.pad_char.text() or ' '
        length = self.pad_length.value()
        self.result_text.setText(text.ljust(length, char[0]))

    def concat(self):
        text = self.get_selected_text()
        add_text = self.concat_text.text()
        self.result_text.setText(text + add_text)

    def concat_operator(self):
        text = self.get_selected_text()
        add_text = self.concat_text.text()
        self.result_text.setText(f"{text} || {add_text}")

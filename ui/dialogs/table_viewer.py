from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox

class TableViewerDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Обозреватель таблиц (динамич.)")
        self.setMinimumSize(900, 600)
        self.setup_ui()
        self.load_tables()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Таблица:"))
        self.table_combo = QComboBox()
        top.addWidget(self.table_combo)

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.refresh_table)
        top.addWidget(refresh_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        top.addWidget(close_btn)

        layout.addLayout(top)

        self.table_widget = QTableWidget()
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_widget)

        self.table_combo.currentTextChanged.connect(self.refresh_table)

    def load_tables(self):
        tables = self.controller.get_tables() or []
        self.table_combo.clear()
        self.table_combo.addItems(tables)
        if tables:
            self.refresh_table()

    def refresh_table(self):
        table = self.table_combo.currentText()
        if not table:
            return

        try:
            query = f"SELECT * FROM {table} ORDER BY 1"
            rows = self.controller.execute_custom_request(query)

            self.table_widget.clear()

            if not rows:
                columns = self.controller.get_table_columns(table) or []
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(len(columns))
                self.table_widget.setHorizontalHeaderLabels(columns)
                return

            columns = list(rows[0].keys())
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)

            self.table_widget.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, col in enumerate(columns):
                    val = row.get(col)
                    self.table_widget.setItem(i, j, QTableWidgetItem("" if val is None else str(val)))
        except Exception as e:
            # Доп. страховка: на случай, если вызвали не через execute_custom_request
            try:
                if hasattr(self.controller, "connection") and self.controller.connection:
                    self.controller.connection.rollback()
            except Exception:
                pass
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить таблицу:\n{e}")
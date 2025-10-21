"""
Централизованные стили для приложения
"""

# Светлая тема
LIGHT_THEME = """
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
QTableWidget {
    border: 1px solid #d0d0d0;
    gridline-color: #e0e0e0;
}
QTableWidget::item:selected {
    background-color: #d0e8ff;
}
"""

# Темная тема
DARK_THEME = """
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
"""

# Стили компонентов
BUTTON_STYLE = """
QPushButton {
    background-color: green;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #228B22;
}
QPushButton:pressed {
    background-color: #32CD32;
}
"""

FORM_LABEL_STYLE = "color: #333333; font-weight: bold;"

INPUT_FIELD_STYLE = """
QLineEdit {
    background-color: white;
    color: #333333;
    border: 1px solid #c0c0c0;
    padding: 4px;
    min-width: 120px;
}
"""

MESSAGE_BOX_STYLE = """
QMessageBox {
    background-color: #f5f5f5;
}
QMessageBox QLabel {
    color: #333333;
}
QMessageBox QPushButton {
    background-color: green;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-weight: bold;
    min-width: 40px;
    min-height: 20px;
}
QMessageBox QPushButton:hover {
    background-color: #228B22;
}
"""
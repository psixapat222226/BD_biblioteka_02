import re
from PySide6.QtWidgets import QTableWidgetItem, QLineEdit


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

class ValidatedLineEdit(QLineEdit):
    """
    Поле ввода с валидацией текста.
    Разрешает только определенные символы, заданные в контроллере.
    """

    def __init__(self, controller, *args, **kwargs):
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

        # Если текст пустой, разрешаем его
        if not new_text or TextValidator.is_valid_text_input(new_text):
            return

        # Если текст не валиден, восстанавливаем старый текст
        self.setText(old_text)
        self.setCursorPosition(cursor_pos)


class TextValidator:
    """Класс для валидации текстовых входных данных."""

    @staticmethod
    def is_valid_text_input(text):
        """
        Проверка валидности текстового ввода.
        Разрешены только буквы (кириллица и латиница), цифры и пробелы.

        Args:
            text (str): Текст для проверки

        Returns:
            bool: True если текст валиден, False в противном случае
        """
        return bool(re.match(r'^[а-яА-Яa-zA-Z0-9\s]*$', text))

class RequestBuilder: #Класс для построения SQL-запросов (запросов к БД)
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._select = []
        self._from = ""
        self._where = []
        self._order_by = []
        self._group_by = []
        self._having = []
        self._aggregate = None
    
    def select(self, columns):
        if isinstance(columns, str):
            self._select = [columns]
        else:
            self._select = columns
        return self
    
    def from_table(self, table):
        self._from = table
        return self
    
    def where(self, condition):
        self._where.append(condition)
        return self
    
    def order_by(self, column, direction="ASC"):
        self._order_by.append(f"{column} {direction}")
        return self
    
    def group_by(self, column):
        self._group_by.append(column)
        return self
    
    def having(self, condition):
        self._having.append(condition)
        return self
    
    def aggregate(self, function, column):
        self._aggregate = f"{function}({column})"
        return self
    
    def build(self):
        if self._group_by and not self._aggregate:
            self._aggregate = "COUNT(*)"
        if not self._select and not self._aggregate:
            self._select = ["*"]
        
        sql = "SELECT "
        
        if self._aggregate:
            sql += self._aggregate
            if self._select:
                sql += ", " + ", ".join(self._select)
        else:
            sql += ", ".join(self._select) if self._select else "*"
        
        sql += f" FROM {self._from}"
        
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        
        if self._group_by:
            sql += " GROUP BY " + ", ".join(self._group_by)
        
        if self._having:
            sql += " HAVING " + " AND ".join(self._having)
        
        if self._order_by:
            sql += " ORDER BY " + ", ".join(self._order_by)
        
        return sql

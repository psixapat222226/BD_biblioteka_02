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

class RequestBuilder:
    """Класс для построения SQL-запросов с поддержкой сложных конструкций"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._select = []
        self._from = ""
        self._where = []
        self._order_by = []
        self._group_by = []
        self._having = []
        self._aggregates = []
        self._joins = []
    
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
    
    def aggregate_custom(self, aggregate_expression):
        """Добавляет произвольное агрегатное выражение"""
        self._aggregates.append(aggregate_expression)
        return self
    
    def join(self, table, condition, join_type="INNER"):
        """Добавляет JOIN"""
        self._joins.append(f"{join_type} JOIN {table} ON {condition}")
        return self
    
    def build(self):
        """Построение итогового SQL-запроса"""
        sql_parts = []
        
        # SELECT часть
        select_parts = []
        
        # Добавляем обычные столбцы
        if self._select:
            select_parts.extend(self._select)
        
        # Добавляем агрегатные функции
        if self._aggregates:
            select_parts.extend(self._aggregates)
        
        if not select_parts:
            select_parts = ["*"]
        
        sql_parts.append(f"SELECT {', '.join(select_parts)}")
        
        # FROM часть
        if self._from:
            sql_parts.append(f"FROM {self._from}")
        
        # JOIN части
        if self._joins:
            sql_parts.extend(self._joins)
        
        # WHERE часть
        if self._where:
            sql_parts.append(f"WHERE {' AND '.join(self._where)}")
        
        # GROUP BY часть
        if self._group_by:
            sql_parts.append(f"GROUP BY {', '.join(self._group_by)}")
        
        # HAVING часть
        if self._having:
            sql_parts.append(f"HAVING {' AND '.join(self._having)}")
        
        # ORDER BY часть
        if self._order_by:
            sql_parts.append(f"ORDER BY {', '.join(self._order_by)}")
        
        return " ".join(sql_parts)

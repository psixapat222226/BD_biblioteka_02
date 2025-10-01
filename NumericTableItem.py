
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


"""
Модуль управления театральными постановками.
Содержит основную бизнес-логику приложения.
"""
import random
import re
from data import DatabaseManager
from logger import Logger


class Controller:
    """
    Основной контроллер театра, отвечающий за бизнес-логику приложения.
    Управляет актерами, постановками, бюджетом и результатами спектаклей.
    """
    def __init__(self):
        """Инициализация контроллера."""
        self.db = DatabaseManager()
        self.logger = Logger()
        self.is_connected = False

    def set_connection_params(self, dbname, user, password, host, port):
        """Установка параметров подключения к БД."""
        self.db.set_connection_params(dbname, user, password, host, port)

    def connect_to_database(self):
        """Установка соединения с БД."""
        self.is_connected = self.db.connect()
        return self.is_connected

    def create_database(self):
        """Создание новой базы данных."""
        return self.db.create_database()

    def initialize_database(self):
        """Инициализация схемы БД и заполнение тестовыми данными."""
        result1 = self.db.create_schema()
        result2 = self.db.init_sample_data()
        return result1 and result2

    def reset_database(self):
        """Сброс данных БД к начальному состоянию."""
        return self.db.reset_database()

    def reset_schema(self):
        """Сброс схемы БД и пересоздание всех таблиц."""
        return self.db.reset_schema()

    def get_all_readers(self):
        """Получение списка всех актеров."""
        return self.db.get_readers()

    def get_all_books(self):
        """Получение списка всех книг"""
        return self.db.get_books()

    def get_all_issues(self):
        """Получение списка всех заказов"""
        return self.db.get_issues()

    def get_all_book_authors(self):
        """Получение списка всех книг и авторов"""
        return self.db.get_book_authors()

    def get_all_authors(self):
        """Получение истории всех авторов"""
        return self.db.get_authors()

    def add_new_reader(self, last_name, first_name, patronymic, ticket_number, registration_date):
        """Добавление нового читателя в базу данных."""
        return self.db.add_reader(last_name, first_name, patronymic, ticket_number, registration_date)

    def add_new_book(self, title, publication_year, genre, isbn, available_copies):
        """Добавление новой книги в базу данных."""
        return self.db.add_book(title, publication_year, genre, isbn, available_copies)

    def add_new_issue(self, book_id, reader_id, issue_date, return_date):
        """Добавление нового заказа (выдачи книги) в базу данных."""
        return self.db.add_issue(book_id, reader_id, issue_date, return_date)

    def add_new_book_author(self, book_id, author_id):
        """Добавление новой связи книга–автор в базу данных."""
        return self.db.add_book_author(book_id, author_id)

    def add_new_author(self, last_name, first_name, patronymic, birth_year, country):
        """Добавление нового автора в базу данных."""
        return self.db.add_author(last_name, first_name, patronymic, birth_year, country)

    def update_reader(self, reader_id, last_name, first_name, patronymic, ticket_number, registration_date):
        """Обновление данных читателя."""
        return self.db.update_reader(reader_id, last_name, first_name, patronymic, ticket_number, registration_date)

    def update_book(self, book_id, title, publication_year, genre, isbn, available_copies):
        """Обновление данных книги."""
        return self.db.update_book(book_id, title, publication_year, genre, isbn, available_copies)

    def update_issue(self, issue_id, book_id, reader_id, issue_date, return_date):
        """Обновление данных заказа (выдачи книги)."""
        return self.db.update_issue(issue_id, book_id, reader_id, issue_date, return_date)

    def update_book_author(self, old_book_id, old_author_id, new_book_id, new_author_id):
        """Обновление связи книга–автор в базе данных."""
        return self.db.update_book_author(old_book_id, old_author_id, new_book_id, new_author_id)

    def delete_reader_by_id(self, reader_id):
        """Удаление читателя по его ID."""
        return self.db.delete_reader(reader_id)

    def delete_book_author_by_id(self, book_id, author_id):
        """Удаление связи книга–автор по ключу (book_id, author_id)."""
        return self.db.delete_book_author(book_id, author_id)

    def delete_book_by_id(self, book_id):
        """Удаление книгу по ID"""
        return self.db.delete_book(book_id)

    def delete_issue_by_id(self, issue_id):
        """Удаление зазак по ID"""
        return self.db.delete_issue(issue_id)

    def is_valid_text_input(self, text):
        """
        Проверка валидности текстового ввода.
        Разрешены только буквы, цифры и пробелы.
        """
        return bool(re.match(r'^[а-яА-Яa-zA-Z0-9\s]*$', text))

    def update_author(self, author_id, last_name, first_name, patronymic, birth_year, country):
        return self.db.update_author(author_id, last_name, first_name, patronymic, birth_year, country)

    def close(self):
        """Закрытие соединения с БД."""
        self.db.disconnect()

    def delete_author_by_id(self, author_id):
        return self.db.delete_author(author_id)
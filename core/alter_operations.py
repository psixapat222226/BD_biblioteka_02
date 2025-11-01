import psycopg2
from typing import Tuple, List, Optional
from PySide6.QtWidgets import QMessageBox


class AlterTableManager:
    """
    Менеджер для выполнения операций ALTER TABLE.
    Полностью совместим с существующей архитектурой приложения.
    """

    def __init__(self, db_connection):
        self.conn = db_connection

    def execute_safe(self, sql: str, params: tuple = None) -> Tuple[bool, str]:
        """
        Безопасное выполнение SQL-запроса с обработкой ошибок и транзакционностью.
        """
        try:
            with self.conn.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                self.conn.commit()
                return True, "Операция выполнена успешно"
        except psycopg2.Error as e:
            self.conn.rollback()
            error_msg = f"Ошибка базы данных: {e}"
            return False, error_msg
        except Exception as e:
            self.conn.rollback()
            error_msg = f"Неожиданная ошибка: {e}"
            return False, error_msg

    def get_tables(self) -> List[str]:
        """Получить список всех таблиц в базе данных."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении списка таблиц: {e}")
            return []

    def get_table_columns(self, table: str) -> List[Tuple]:
        """Получить информацию о столбцах таблицы."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, (table,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении столбцов таблицы {table}: {e}")
            return []

    def get_table_constraints(self, table: str) -> List[Tuple]:
        """Получить ограничения таблицы."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT constraint_name, constraint_type
                    FROM information_schema.table_constraints
                    WHERE table_name = %s
                """, (table,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении ограничений таблицы {table}: {e}")
            return []

    # Основные операции ALTER TABLE
    def add_column(self, table: str, column: str, data_type: str,
                   nullable: bool = True, default: str = None) -> Tuple[bool, str]:
        """Добавить новый столбец в таблицу."""
        nullable_clause = "" if nullable else " NOT NULL"
        default_clause = f" DEFAULT {default}" if default else ""

        sql = f"ALTER TABLE {table} ADD COLUMN {column} {data_type}{nullable_clause}{default_clause}"
        return self.execute_safe(sql)

    def drop_column(self, table: str, column: str) -> Tuple[bool, str]:
        """Удалить столбец из таблицы."""
        sql = f"ALTER TABLE {table} DROP COLUMN {column} CASCADE"
        return self.execute_safe(sql)

    def rename_table(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        """Переименовать таблицу."""
        sql = f"ALTER TABLE {old_name} RENAME TO {new_name}"

        return self.execute_safe(sql)


    def rename_column(self, table: str, old_name: str, new_name: str) -> Tuple[bool, str]:
        """Переименовать столбец в таблице."""
        sql = f"ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name}"
        return self.execute_safe(sql)

    def modify_column_type(self, table: str, column: str, new_type: str) -> Tuple[bool, str]:
        """Изменить тип данных столбца."""
        sql = f"ALTER TABLE {table} ALTER COLUMN {column} TYPE {new_type}"
        return self.execute_safe(sql)

    def add_constraint(self, table: str, constraint_type: str,
                       constraint_name: str, definition: str) -> Tuple[bool, str]:
        """Добавить ограничение к таблице."""
        sql = f"ALTER TABLE {table} ADD CONSTRAINT {constraint_name} {constraint_type} ({definition})"
        return self.execute_safe(sql)

    def drop_constraint(self, table: str, constraint_name: str) -> Tuple[bool, str]:
        """Удалить ограничение из таблицы."""
        sql = f"ALTER TABLE {table} DROP CONSTRAINT {constraint_name}"
        return self.execute_safe(sql)

    def set_column_nullable(self, table: str, column: str, nullable: bool) -> Tuple[bool, str]:
        """Установить или снять ограничение NOT NULL."""
        action = "DROP NOT NULL" if nullable else "SET NOT NULL"
        sql = f"ALTER TABLE {table} ALTER COLUMN {column} {action}"
        return self.execute_safe(sql)

    def add_foreign_key(self, table: str, column: str,
                        reference_table: str, reference_column: str,
                        constraint_name: str = None) -> Tuple[bool, str]:
        """Добавить внешний ключ."""
        name = constraint_name or f"fk_{table}_{column}"
        sql = f"ALTER TABLE {table} ADD CONSTRAINT {name} " \
              f"FOREIGN KEY ({column}) REFERENCES {reference_table}({reference_column})"
        return self.execute_safe(sql)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной файл запуска BookBot.
"""

import sys
import os
import argparse

# Добавляем текущую директорию в пути Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def main():
    parser = argparse.ArgumentParser(description="BookBot - система управления книгами")
    parser.add_argument('--test', action='store_true', help='Запуск тестового режима')
    parser.add_argument('--db-path', default='data/books.db', help='Путь к базе данных')
    parser.add_argument('command', nargs='?', help='Команда CLI')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    
    args = parser.parse_args()
    
    # Создаем папку для данных
    os.makedirs(os.path.dirname(args.db_path), exist_ok=True)
    
    if args.test:
        run_test_mode(args.db_path)
    elif args.command:
        run_cli_mode(args.command, args.args, args.db_path)
    else:
        print("Используйте --help для просмотра команд")


def run_test_mode(db_path):
    """Тестовый режим."""
    print("=" * 60)
    print("ТЕСТОВЫЙ РЕЖИМ BOOKBOT")
    print("=" * 60)
    
    try:
        from bookbot.database import DatabaseManager
        print("[OK] Модуль database загружен")
        
        db = DatabaseManager(db_path)
        print("[OK] База данных создана")
        
        # Тест 1: Добавление книги
        print("\n1. Тест добавления книги:")
        try:
            book_id = db.add_book("Война и мир", "Лев Толстой", "Роман")
            print(f"   Книга добавлена, ID: {book_id}")
        except Exception as e:
            print(f"   Ошибка добавления: {e}")
        
        # Тест 2: Получение книги
        print("\n2. Тест получения книги:")
        if 'book_id' in locals():
            book = db.get_book(book_id)
            if book:
                print(f"   Найдена книга: '{book.get('title', '')}'")
                print(f"   Длина заголовка: {len(book.get('title', ''))}")
            else:
                print("   Книга не найдена")
        
        # Тест 3: Поиск
        print("\n3. Тест поиска:")
        results = db.search_books('author', 'Толстой')
        print(f"   Найдено книг: {len(results)}")
        
        # Тест 4: Все книги
        print("\n4. Все книги в базе:")
        all_books = db.get_all_books()
        print(f"   Всего записей: {len(all_books)}")
        
        print("\n" + "=" * 60)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 60)
        
    except ImportError as e:
        print(f"[ERROR] Ошибка импорта: {e}")
        print("\nСовет: Убедитесь, что в папке bookbot/ есть файл database.py")
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")


def run_cli_mode(command, cmd_args, db_path):
    """CLI режим."""
    print("CLI режим пока не реализован")
    print(f"Команда: {command}, аргументы: {cmd_args}")


if __name__ == "__main__":
    main()

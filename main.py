#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной файл запуска BookBot.
"""

import sys
import argparse
import os


def main():
    """Основная функция запуска."""
    parser = argparse.ArgumentParser(
        description="BookBot - система управления книгами",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  1. CLI режим:
     python main.py add "Война и мир" "Лев Толстой" "Роман"
     python main.py search author "Толстой"
     python main.py top rating --limit 5

  2. Telegram бот:
     python main.py --telegram --token "ВАШ_ТОКЕН"

  3. Тестирование:
     python main.py --test
        """
    )
    
    # Основные аргументы
    parser.add_argument('--telegram', action='store_true', help='Запуск Telegram бота')
    parser.add_argument('--token', help='Токен Telegram бота (требуется с --telegram)')
    parser.add_argument('--db-path', default='data/books.db', help='Путь к базе данных')
    parser.add_argument('--test', action='store_true', help='Запуск тестового режима')
    
    # Аргументы для CLI
    parser.add_argument('command', nargs='?', help='Команда CLI (add, search, top)')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Аргументы команды')
    
    args = parser.parse_args()
    
    # Создаем папку для данных если её нет
    os.makedirs(os.path.dirname(args.db_path), exist_ok=True)
    
    # Проверяем режим работы
    if args.telegram:
        # Запуск Telegram бота
        if not args.token:
            print("Ошибка: для запуска Telegram бота требуется --token")
            sys.exit(1)
        
        try:
            from bookbot.telegram_bot_simple import run_simple_bot
            run_simple_bot()
        except ImportError:
            print("Ошибка: модуль telegram_bot_simple не найден")
            print("Создайте файл bookbot/telegram_bot_simple.py")
            sys.exit(1)
            
    elif args.test:
        # Тестовый режим
        run_test_mode(args.db_path)
        
    elif args.command:
        # CLI режим
        run_cli_mode(args.command, args.args, args.db_path)
        
    else:
        # Интерактивный режим
        run_interactive_mode(args.db_path)


def run_test_mode(db_path):
    """Тестовый режим."""
    print("=" * 60)
    print("ТЕСТОВЫЙ РЕЖИМ BOOKBOT")
    print("=" * 60)
    
    try:
        from bookbot.database import DatabaseManager
        from bookbot.search import BookSearch
        from bookbot.cli import BookBotCLI
        
        print("✅ Все модули загружены успешно")
        
        # Тест базы данных
        print("\n1. Тестирование базы данных:")
        db = DatabaseManager(db_path)
        
        # Добавляем тестовые данные
        test_books = [
            ("Война и мир", "Лев Толстой", "Роман"),
            ("1984", "George Orwell", "Антиутопия"),
            ("Преступление и наказание", "Фёдор Достоевский", "Классика"),
        ]
        
        for title, author, genre in test_books:
            try:
                book_id = db.add_book(title, author, genre)
                print(f"   Добавлено: '{title}' (ID: {book_id})")
            except Exception as e:
                print(f"   Ошибка добавления '{title}': {e}")
        
        # Тест поиска
        print("\n2. Тестирование поиска:")
        search = BookSearch(db)
        results = search.search_with_stats("author", "Толстой")
        print(f"   Найдено книг по автору 'Толстой': {len(results)}")
        
        # Тест CLI
        print("\n3. Тестирование CLI:")
        cli = BookBotCLI(db_path)
        
        # Тест команды add
        print("   Тест команды 'add':")
        test_args = ["add", "Тестовая книга", "Тестовый автор", "Тест"]
        cli.run(test_args)
        
        # Тест команды search
        print("\n   Тест команды 'search':")
        test_args = ["search", "author", "Толстой"]
        cli.run(test_args)
        
        print("\n" + "=" * 60)
        print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
        print("=" * 60)
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь что все модули созданы:")
        print("  - bookbot/database.py")
        print("  - bookbot/search.py")
        print("  - bookbot/cli.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def run_cli_mode(command, cmd_args, db_path):
    """CLI режим."""
    try:
        from bookbot.cli import BookBotCLI
        
        cli = BookBotCLI(db_path)
        
        # Собираем все аргументы
        all_args = [command] + cmd_args
        sys.exit(cli.run(all_args))
        
    except ImportError:
        print("Ошибка: модуль cli не найден")
        print("Создайте файл bookbot/cli.py")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


def run_interactive_mode(db_path):
    """Интерактивный режим."""
    print("=" * 50)
    print("BOOKBOT - система управления книгами")
    print("=" * 50)
    print("\nДоступные режимы:")
    print("  1. CLI (командная строка)")
    print("  2. Telegram бот")
    print("  3. Тестирование")
    print("  4. Выход")
    
    try:
        choice = input("\nВыберите режим (1-4): ").strip()
        
        if choice == "1":
            print("\nИспользование CLI:")
            print("  python main.py add 'Название' 'Автор' 'Жанр'")
            print("  python main.py search author 'Толстой'")
            print("  python main.py top rating --limit 5")
            
        elif choice == "2":
            print("\nДля запуска Telegram бота:")
            print("  1. Получите токен у @BotFather")
            print("  2. Запустите: python main.py --telegram --token 'ВАШ_ТОКЕН'")
            
        elif choice == "3":
            run_test_mode(db_path)
            
        elif choice == "4":
            print("Выход...")
            
        else:
            print("Неверный выбор")
            
    except KeyboardInterrupt:
        print("\nВыход...")


if __name__ == "__main__":
    main()

import logging
import argparse
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
from telegram.constants import ParseMode

EMOJI = {
    "search": "🔍", "star": "⭐️", "fire": "🔥", "trophy": "🏆", "plus": "➕",
    "list": "📋", "help": "❓", "back": "↩️", "home": "🏠", "check": "✅",
    "cross": "❌", "book": "📚", "user": "👤", "pencil": "✏️", "bookshelf": "📖"
}

CHOOSING, TYPING_SEARCH, TYPING_BOOK_INFO = range(3)

class BookBot:
    def __init__(self, token: str):  # Исправлено: init -> __init__
        self.token = token
        self.application = None
        
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)  # Исправлено: name -> __name__

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start."""
        welcome_text = f"""
{EMOJI['book']} <b>Привет!</b>

Я <b>BookBot</b> - помощник для книг.

<b>Что умею:</b>
{EMOJI['search']} Искать книги
{EMOJI['plus']} Добавлять книги
{EMOJI['list']} Вести список
{EMOJI['trophy']} Показывать топы

Выберите действие:
        """
        
        keyboard = [
            [KeyboardButton(f"{EMOJI['search']} Поиск"), KeyboardButton(f"{EMOJI['trophy']} Топ")],
            [KeyboardButton(f"{EMOJI['plus']} Добавить"), KeyboardButton(f"{EMOJI['list']} Список")],
            [KeyboardButton(f"{EMOJI['help']} Помощь")]
        ]
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        return CHOOSING

    async def help_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help."""
        help_text = f"""
{EMOJI['help']} <b>Помощь</b>

Команды:
/start - Начать
/search - Поиск книг
/add - Добавить книгу
/mybooks - Мой список
/top - Топ книг

Формат добавления:
<code>Название | Автор | Жанр</code>
Пример: <code>Властелин колец | Толкин | Фэнтези</code>
        """
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

    async def search_books(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Поиск книг."""
        keyboard = [
            [InlineKeyboardButton("По названию", callback_data='title'),
             InlineKeyboardButton("По автору", callback_data='author')],
            [InlineKeyboardButton("По жанру", callback_data='genre'),
             InlineKeyboardButton("Назад", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(f"{EMOJI['search']} <b>Выберите тип поиска:</b>",
                                       parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        return TYPING_SEARCH

    async def add_book(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавить книгу."""
        await update.message.reply_text(
            f"{EMOJI['plus']} <b>Введите книгу в формате:</b>\n"
            "<code>Название | Автор | Жанр</code>\n\n"
            "<i>Пример: Властелин колец | Толкин | Фэнтези</i>",
            parse_mode=ParseMode.HTML
        )
        return TYPING_BOOK_INFO

    async def my_books(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Мой список."""
        await update.message.reply_text(
            f"{EMOJI['list']} <b>Ваш список пуст.</b>\n"
            f"{EMOJI['plus']} Добавьте книги через поиск или вручную.",
            parse_mode=ParseMode.HTML
        )

    async def top_books(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Топ книг."""
        keyboard = [
            [InlineKeyboardButton(f"{EMOJI['star']} По рейтингу", callback_data='rating'),
             InlineKeyboardButton(f"{EMOJI['fire']} По популярности", callback_data='popular')],
            [InlineKeyboardButton("Назад", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(f"{EMOJI['trophy']} <b>Топ книг:</b>",
                                       parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопок."""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'back':
            await self.back_to_menu(update, context)
        else:
            await query.edit_message_text(
                f"{EMOJI['check']} <b>Функция в разработке</b>\n"
                f"Тип: {query.data}",
                parse_mode=ParseMode.HTML
            )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текста."""
        text = update.message.text
        
        if "|" in text:
            # Добавление книги
            try:
                title, author, genre = [x.strip() for x in text.split("|")]
                await update.message.reply_text(
                    f"{EMOJI['check']} <b>Книга добавлена!</b>\n"
                    f"{EMOJI['bookshelf']} <b>{title}</b>\n"
                    f"{EMOJI['user']} {author}\n"
                    f"{EMOJI['pencil']} {genre}",
                    parse_mode=ParseMode.HTML
                )
                return CHOOSING
            except:
                await update.message.reply_text(
                    f"{EMOJI['cross']} <b>Ошибка формата</b>\n"
                    "Используйте: Название | Автор | Жанр",
                    parse_mode=ParseMode.HTML
                )
        else:
            # Поиск
            await update.message.reply_text(
                f"{EMOJI['search']} <b>Поиск:</b> {text}\n"
                "Результаты в разработке...",
                parse_mode=ParseMode.HTML
            )
            return CHOOSING

    async def back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Вернуться в меню."""
        keyboard = [
            [KeyboardButton(f"{EMOJI['search']} Поиск"), KeyboardButton(f"{EMOJI['trophy']} Топ")],
            [KeyboardButton(f"{EMOJI['plus']} Добавить"), KeyboardButton(f"{EMOJI['list']} Список")],
            [KeyboardButton(f"{EMOJI['help']} Помощь")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        if update.callback_query:
            await update.callback_query.message.reply_text(
                f"{EMOJI['home']} <b>Главное меню</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                f"{EMOJI['home']} <b>Главное меню</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена."""
        await update.message.reply_text(
            f"{EMOJI['cross']} Действие отменено",
            parse_mode=ParseMode.HTML
        )
        await self.back_to_menu(update, context)

    def setup(self):
        """Настройка обработчиков."""
        self.application = Application.builder().token(self.token).build()
        
        # Основной обработчик
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                CHOOSING: [
                    MessageHandler(filters.Regex(f"^{EMOJI['search']} Поиск$"), self.search_books),
                    MessageHandler(filters.Regex(f"^{EMOJI['trophy']} Топ$"), self.top_books),
                    MessageHandler(filters.Regex(f"^{EMOJI['plus']} Добавить$"), self.add_book),
                    MessageHandler(filters.Regex(f"^{EMOJI['list']} Список$"), self.my_books),
                    MessageHandler(filters.Regex(f"^{EMOJI['help']} Помощь$"), self.help_cmd),
                    CallbackQueryHandler(self.handle_callback),
                ],
                TYPING_SEARCH: [
                    CallbackQueryHandler(self.handle_callback),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text),
                ],
                TYPING_BOOK_INFO: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        
        self.application.add_handler(conv_handler)
        self.application.add_handler(CommandHandler("help", self.help_cmd))
        self.application.add_handler(CommandHandler("search", self.search_books))
        self.application.add_handler(CommandHandler("add", self.add_book))
        self.application.add_handler(CommandHandler("mybooks", self.my_books))
        self.application.add_handler(CommandHandler("top", self.top_books))

    def run(self):
        """Запуск бота."""
        self.setup()
        print("🤖 BookBot запущен!")
        print("📱 Перейдите в Telegram и используйте /start")
        self.application.run_polling()


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Telegram BookBot")
    parser.add_argument('--token', help='Токен бота')
    
    args = parser.parse_args()
    
    token = args.token or os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        print("❌ Ошибка: Укажите токен")
        print("   python bot.py --token 'ВАШ_ТОКЕН'")
        print("   или export TELEGRAM_TOKEN='ВАШ_ТОКЕН'")
        sys.exit(1)
    
    bot = BookBot(token)
    bot.run()


if __name__ == "__main__":  # Исправлено: name -> __name__
    main()

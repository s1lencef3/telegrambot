import re

from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler

from user_commands import *
from admin_commands import *
from conversation import *


def command_handler(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_handler(CommandHandler('profile', my_profile))

    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(MessageHandler(Filters.regex('Помощь'), help))

    dispatcher.add_handler(CommandHandler('register', register))

    dispatcher.add_handler(CommandHandler('menu', call_menu))

    dispatcher.add_handler(MessageHandler(Filters.regex('Закрыть меню'), clear))
    dispatcher.add_handler(CommandHandler('clear', clear))

    dispatcher.add_handler(MessageHandler(Filters.regex('Записи лекций'), write_lectures))
    dispatcher.add_handler(CommandHandler('lectures', write_lectures))

    dispatcher.add_handler(MessageHandler(Filters.regex('Задания'), write_task))
    dispatcher.add_handler(CommandHandler('tasks', write_task))

    dispatcher.add_handler(MessageHandler(Filters.regex('Контрольные точки/экзамены'), write_checkpoint))
    dispatcher.add_handler(CommandHandler('checkpoints', write_checkpoint))

    dispatcher.add_handler(MessageHandler(Filters.regex('Дополнительные источники'), write_source))
    dispatcher.add_handler(CommandHandler('sources', write_source))

    dispatcher.add_handler(MessageHandler(Filters.regex('Уведомления'), turn_notifications))
    dispatcher.add_handler(CommandHandler('notifications', turn_notifications))

    dispatcher.add_handler(CommandHandler("admin", admin))
    dispatcher.add_handler(CommandHandler("adminhelp", adminhelp))
    dispatcher.add_handler(CommandHandler("add_group", add_group))

    dispatcher.add_handler(new_task_handler)
    dispatcher.add_handler(new_lecture_handler)
    dispatcher.add_handler(new_checkpoint_handler)
    dispatcher.add_handler(new_source_handler)

    dispatcher.add_handler(MessageHandler(Filters.text, all_messages))

    dispatcher.add_handler(CallbackQueryHandler(btn_handler))

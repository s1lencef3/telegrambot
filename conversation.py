from telegram.ext import MessageHandler, ConversationHandler, CommandHandler, Filters, CallbackQueryHandler
from admin_commands import *

new_task_handler = ConversationHandler(
    entry_points=[CommandHandler('add_task', add_task)],
    states={
        0: [MessageHandler(Filters.text , task_lesson)],
        1: [MessageHandler(Filters.text , task_value)],
        2: [MessageHandler(Filters.text , finish_task)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
new_lecture_handler = ConversationHandler(
    entry_points=[CommandHandler('add_lecture', add_lecture)],
    states={
        0: [MessageHandler(Filters.text, lecture_lesson)],
        1: [MessageHandler(Filters.text, lecture_date)],
        2: [MessageHandler(Filters.text, lecture_value)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
new_checkpoint_handler = ConversationHandler(
    entry_points=[CommandHandler('add_checkpoint', add_checkpoint)],
    states={
        0: [MessageHandler(Filters.text , checkpoint_lesson)],
        1: [CallbackQueryHandler(checkpoint_kind)],
        2: [MessageHandler(Filters.text , finish_checkpoint)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
new_source_handler = ConversationHandler(
    entry_points=[CommandHandler('add_source', add_source)],
    states={
        0: [MessageHandler(Filters.text , source_name)],
        1: [MessageHandler(Filters.text , finish_source)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
from config import *
from command_handler import *
import logging

from telegram import Bot
from telegram.ext import Updater


def main():
    bot = Bot(token=TOKEN)

    print(bot)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    command_handler(dispatcher)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

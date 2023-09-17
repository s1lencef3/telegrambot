import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from telegram.ext import ConversationHandler

from menus import *
from models import *

types = ['source', 'task', 'lecture', 'checkpoint', 'notifications']
kinds = {
    'kt': 'КТ',
    'ex': 'ЭКЗАМЕН'
}


def is_user_exist(id):
    try:
        user = User.get(id=id)
        if not user.id:
            raise DoesNotExist
        return True
    except DoesNotExist:
        return False


def checkuser(function):
    def check(update, context):
        if not is_user_exist(id=update.message.from_user.id):
            if update.message.from_user.username:
                username = update.message.from_user.username
            else:
                username = 'none'

            user = User.create(
                id=update.message.from_user.id,
                status='student',
                name=update.message.from_user.first_name,
                username=username,
                group=0000
            )
            user.save()
        function(update, context)

    return check


def checkadmin(function):
    def check(update, context):
        user = User.get(id=update.message.from_user.id)
        if user.status == 'admin':
            function(update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='неизвестная команда',
                                     parse_mode=telegram.ParseMode.HTML)

    return check


def get_profile(user):
    if user.status == 'student':
        status = 'Студент'
    else:
        status = 'Студент-администратор'
    if user:
        text = f"<b>Профиль</b>\nИмя - {user.name}\n{status}\n<i>Группа: {user.group}</i>"
        return text


def is_number(n):
    if n:
        try:
            int(n)
        except:
            return False
    else:
        return False
    return True


def read_lectures(user):
    lections = Item.select().where(Item.type == types[2])
    text = 'Выберите предмет:\n'
    buttons = []
    lecs = []

    print(lections)

    for lecture in lections:
        if str(lecture.lesson) not in lecs and lecture.group == user.group:
            lecs.append(str(lecture.lesson))
            callback_data = f'lecture#{lecture.lesson}#{lecture.group}'
            buttons.append(InlineKeyboardButton(lecture.lesson, callback_data=callback_data))
    footer_keyboard = [
        InlineKeyboardButton('Вернуться', callback_data='back')
    ]
    print(lecs)
    if len(lecs) == 0:
        text = 'Нет доступных лекций'
    reply_markup = InlineKeyboardMarkup(build_menu(buttons=buttons, n_cols=2, footer_buttons=footer_keyboard))
    return text, reply_markup


def read_tasks(user):
    tasks = Item.select().where(Item.type == types[1])
    text = 'Выберите предмет:\n'
    buttons = []
    ts = []

    print(tasks)

    for task in tasks:
        if str(task.lesson) not in ts and task.group == user.group:
            ts.append(str(task.lesson))
            callback_data = f'task#{task.lesson}#{task.group}'
            buttons.append(InlineKeyboardButton(task.lesson, callback_data=callback_data))
    footer_keyboard = [
        InlineKeyboardButton('Вернуться', callback_data='back')
    ]
    if len(ts) == 0:
        text = 'Нет доступных заданий'
    reply_markup = InlineKeyboardMarkup(build_menu(buttons=buttons, n_cols=2, footer_buttons=footer_keyboard))
    return text, reply_markup


def read_checkpoints(user):
    checkpoints = Item.select().where(Item.type == types[3])
    text = 'Выберите предмет:\n'
    buttons = []
    checks = []

    print(checkpoints)

    for checkpoint in checkpoints:
        if str(checkpoint.lesson) not in checks and checkpoint.group == user.group:
            checks.append(str(checkpoint.lesson))
            callback_data = f'checkpoint#{checkpoint.lesson}#{checkpoint.group}'
            buttons.append(InlineKeyboardButton(checkpoint.lesson, callback_data=callback_data))
    footer_keyboard = [
        InlineKeyboardButton('Вернуться', callback_data='back')
    ]
    if len(checks) == 0:
        text = 'Нет доступных КТ'
    reply_markup = InlineKeyboardMarkup(build_menu(buttons=buttons, n_cols=2, footer_buttons=footer_keyboard))
    return text, reply_markup


def read_sources():
    sources = Item.select().where(Item.type == types[0])
    text = 'Полезные ссылки:\n'

    print(sources)

    for source in sources:
        text += f'{source.id}. {source.lesson} \n' \
                f'Ссылка: {source.value}\n\n'

    return text


def get_item(item):
    text = ''
    if item:
        if str(item.type) == types[0]:
            text = f"<b>{item.lesson}</b>\n\n" \
                   f"Ссылка:  <i>{item.value}</i>\n"
        elif str(item.type) == types[1]:
            text = f"<b>Предмет: #{item.lesson}</b>\n\n" \
                   f"Формулировка задания: <i>{item.value}</i>\n" \
                   f"Дедлайн: <i>{item.date}</i>\n" \
                   f"Для группы: <i>{item.group}</i>\n\n"
        elif str(item.type) == types[2]:
            text = f"<b>Предмет: #{item.lesson}</b>\n\n" \
                   f"Ссылка на запись: <i>{item.value}</i>\n" \
                   f"Для группы: <i>{item.group}</i>\n\n"
        elif str(item.type) == types[3]:
            print(33)
            text = f"<b>Предмет: #{item.lesson}</b>\n\n" \
                   f"Вид: <i>{item.kind}</i>\n" \
                   f"Дата проведения: <i>{item.date}</i>\n" \
                   f"Для группы: <i>{item.group}</i>\n\n"
        return text


def make_notifications_markup():
    buttons = []

    noties = {
        True: 'Включить',
        False: 'Выключить'
    }

    for k in list(noties.keys()):
        callback_data = f'notifications#{k}'
        buttons.append(InlineKeyboardButton(noties[k], callback_data=callback_data))
    footer_keyboard = [
        InlineKeyboardButton('Вернуться', callback_data='back')
    ]

    return InlineKeyboardMarkup(build_menu(buttons=buttons, n_cols=2, footer_buttons=footer_keyboard))


def check_sem(first, second):
    datedelta = str(second.date - first.date).split()
    print(datedelta)
    try:
        days = int(datedelta[0])
    except Exception:
        return 1
    count = 0
    while days > 0:
        days = days - 120
        count += 1
    return count


def notifications_text(id):
    user = User.get(id=id)
    if user.notifications:
        return 'Уведомления включены'
    else:
        return 'Уведомления выключены'


def end_conversation_chat(update, context):
    text = "Я не знаю как на это ответить. Воспользуйтесь разделом 'Помощь' (/help)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                             reply_markup=get_menu('main').reply_markup,
                             parse_mode=ParseMode.HTML)

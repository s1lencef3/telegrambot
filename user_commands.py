import telegram

from core import *
from telegram import ParseMode, ReplyKeyboardRemove
from menus import *


@checkuser
def start(update, context):
    print(update, context)
    text = 'Здравствуйте! Вас приветствует бот-помощник!\n Я постараюсь максимально облегчить вашу и без того ' \
           'трудную жизнь в наешм чудесном университете\n Для просмотра моих возможностей введите <code>/help</code>\n' \
           'Введите <code>/register номер группы пароль</code> для продолжения и регистрации\n (Пример: ' \
           '<code>/register 1371 1234</code>)\n '
    context.bot.send_message(text=text, chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML)


@checkuser
def help(update, context):
    text = '<b>Список доступных комманд:</b>\n\n' \
           '◊ Чтобы изменить номер группы \n<code>/register номер группы пароль</code>\n (Пример: <code>/register 1371 ' \
           '1234</code>)\n\n' \
           '◊ Чтобы посмотреть данные профиля\n<code>/profile</code> \n\n' \
           '◊ Чтобы очистить меню \n<code>/clear</code> \n\n' \
           '◊ Чтобы вызввать меню  \n<code>/menu</code>\n\n' \
           '◊ Для просмотра записей лекций\n<code>/lectures</code> \n\n' \
           '◊ Для просмотра заданий \n<code>/tasks</code> \n\n' \
           '◊ Чтобы просмотреть контрольные точки \n<code>/checkpoints</code> \n\n' \
           '◊ Чтобы просмотреть полезные источники \n<code>/sources</code> \n\n' \
           '◊ Чтобы включить/выключить уведомления \n<code>/notifications</code> \n\n' \
           '<b>Так же все эти команды дроступны через кнопки меню</b>'
    menu = get_menu('main')
    context.bot.send_message(text=text, reply_markup=menu.reply_markup, chat_id=update.effective_chat.id,
                             parse_mode=ParseMode.HTML)


@checkuser
def my_profile(update, context):
    user = User.get(id=update.message.from_user.id)
    print(f'user {user.id} triggered his profile')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=get_profile(user),
                             parse_mode=ParseMode.HTML)


@checkuser
def all_messages(update, context):
    text = "Я не знаю как на это ответить. Воспользуйтесь разделом 'Помощь' (/help)"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             reply_markup=get_menu('main').reply_markup,
                             parse_mode=ParseMode.HTML)


@checkuser
def register(update, context):
    user = User.get(id=update.message.from_user.id)
    print(user.id)
    menu = get_menu('main')
    reply_markup = None
    text = ' '
    if len(context.args) != 0:
        if is_number(context.args[0]):
            try:
                group = Group.get(number=int(context.args[0]))
                if group.password == context.args[1]:
                    if user.group:
                        print('group changed')
                        text = f'Номер группы изменен с {user.group} на {context.args[0]}'
                        reply_markup = None

                        user.group = context.args[0]
                    elif not user.group:
                        print('group written')
                        user.group = context.args[0]
                        text = 'Номер группы успешно записан'
                        reply_markup = menu.reply_markup

                else:
                    print('wrong password')
                    text = 'Неверный пароль!'
                    reply_markup = None
            except Exception as Err:
                print(Err)
                text = 'Ваша группа еще не подключена к функционалу бота, обратитесь к старосте или создателю бота <code>@silence_f3</code>'

        else:
            print('group not number')
            text = 'Номер группы введен некорректно, воспользуйтесь образцом: <code>/register 1371 1234</code>,\n' \
                   'где вместо 1371 надо записать номер вашей группы\n' \
                   'а вместо 1234 - пароль, сообщенный вам старостой'
            reply_markup = None

    else:
        print('no arguments')
        reply_markup = None
        text = 'Команда введена неверно, воспользуйтесь образцом: <code>/register 1371 1234</code>,\n' \
               'где вместо 1371 надо записать номер вашей группы\n' \
               'а вместо 1234 - пароль, сообщенный вам старостой'

    context.bot.send_message(text=text, reply_markup=reply_markup,
                             chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML)
    user.save()


@checkuser
def call_menu(update, context):
    print(f'menu triggered by{update.message.from_user.id}')
    menu = get_menu('main')
    context.bot.send_message(text='Вызвано меню', reply_markup=menu.reply_markup,
                             chat_id=update.effective_chat.id)


@checkuser
def clear(update, context):
    print(f'menu cleared by{update.message.from_user.id}')
    replay_markup = ReplyKeyboardRemove()
    context.bot.send_message(text='Меню очищено', reply_markup=replay_markup,
                             chat_id=update.effective_chat.id)


@checkuser
def write_lectures(update, context):
    print(f'lectures triggered by {update.message.from_user.id}\n {update}')
    context.user_data['user'] = User.get(id=update.message.from_user.id)
    text, reply_markup = read_lectures(context.user_data['user'])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             parse_mode=ParseMode.HTML,
                             reply_markup=reply_markup)


@checkuser
def write_task(update, context):
    print(f'tasks triggered by {update.message.from_user.id}\n {update}')
    context.user_data['user'] = User.get(id=update.message.from_user.id)
    text, reply_markup = read_tasks(context.user_data['user'])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             parse_mode=ParseMode.HTML,
                             reply_markup=reply_markup)


@checkuser
def write_checkpoint(update, context):
    print(f'checkpoints triggered by {update.message.from_user.id}\n {update}')
    context.user_data['user'] = User.get(id=update.message.from_user.id)
    text, reply_markup = read_checkpoints(context.user_data['user'])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             parse_mode=ParseMode.HTML,
                             reply_markup=reply_markup)


@checkuser
def write_source(update, context):
    print(f'sources triggered by {update.message.from_user.id}\n {update}')
    text = read_sources()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             parse_mode=ParseMode.HTML
                             )


@checkuser
def turn_notifications(update, context):
    context.user_data['id'] = update.message.from_user.id
    print(str(context.user_data['id']) + 'triggered notifications')

    context.user_data['n_text'] = notifications_text(update.message.from_user.id)
    reply_markup = make_notifications_markup()

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=context.user_data['n_text'],
                             reply_markup=reply_markup,
                             parse_mode=ParseMode.HTML
                             )


def btn_handler(update, context):
    query = update.callback_query
    print(update)
    print(context)
    args = query.data.split('#')
    print(args)
    if args[0] == types[2]:
        if args[1] != 'back':
            lesson = args[1]
            group = args[2]
            lectures = Item.select().where(Item.type == types[2]).order_by(Item.date)
            first = Item.get(type=types[2], lesson=lesson, number=1)

            text = f'Записи лекций по предмету {lesson}:\n'
            count = 0

            for lecture in lectures:

                if str(lecture.lesson) == lesson and str(lecture.group) == group:
                    if check_sem(first, lecture) > count:
                        count = check_sem(first, lecture)
                        string = '\n' + '-' * 10 + f' {count} Cеместр ' + '-' * 10 + '\n\n'
                        text += '<b>' + string + '</b>'
                    text += f"Лекция {lecture.number} - {lecture.value}\n"

            button = [InlineKeyboardButton('Вернуться', callback_data='lecture#back')]

            reply_markup = InlineKeyboardMarkup(build_menu(buttons=button, n_cols=1))
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            text, reply_markup = read_lectures(context.user_data['user'])
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    elif args[0] == types[1]:
        if args[1] != 'back':
            lesson = args[1]
            group = args[2]
            tasks = Item.select().where(Item.type == types[1])
            text = f'Задания по предмету {lesson}:\n'
            i = 1
            for task in tasks:
                if str(task.lesson) == lesson and str(task.group) == group:
                    text += f"Задание {i}: {task.value}\n " \
                            f"До {task.date}\n\n"
                    i += 1

            button = [InlineKeyboardButton('Вернуться', callback_data='task#back')]
            reply_markup = InlineKeyboardMarkup(build_menu(buttons=button, n_cols=1))
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            text, reply_markup = read_tasks(context.user_data['user'])
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    elif args[0] == types[3]:

        if args[1] == 'back':
            text, reply_markup = read_checkpoints(context.user_data['user'])
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

        else:

            lesson = args[1]
            group = args[2]
            checkpoints = Item.select().where(Item.type == types[3])
            text = f'Контрольные точки по предмету {lesson}:\n'
            i = 1
            for checkpoint in checkpoints:
                if str(checkpoint.lesson) == lesson and str(checkpoint.group) == group:
                    text += f" {i}: {checkpoint.kind}\n " \
                            f"Дата проведения: {checkpoint.date}\n\n"
                    i += 1

            button = [InlineKeyboardButton('Вернуться', callback_data='checkpoint#back')]
            reply_markup = InlineKeyboardMarkup(build_menu(buttons=button, n_cols=1))
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    elif args[0] == types[4]:
        id = int(context.user_data['id'])
        user = User.get(id=id)
        text = notifications_text(id)
        reply_markup = make_notifications_markup()
        if args[1] == 'True':
            user.notifications = 1
            text = 'Уведомления включены'
        elif args[1] == 'False':
            user.notifications = 0
            text = 'Уведомления выключены'
        if text == context.user_data['n_text']:
            pass
        else:
            context.user_data['n_text'] = text
            query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

        user.save()

    elif args[0] == 'back':
        text = 'Воспользуйтесь командой <code>/help</code> или кнопками Главного меню'
        context.user_data.clear()
        query.edit_message_text(text=text, parse_mode=ParseMode.HTML)


@checkuser
def all_messages(update, context):
    print('unknown command')
    text = "Я не знаю как на это ответить. Воспользуйтесь разделом 'Помощь' (/help)"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             reply_markup=get_menu('main').reply_markup,
                             parse_mode=ParseMode.HTML)

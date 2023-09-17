from config import *
from core import *


@checkuser
def admin(update, context):
    user = User.get(id=update.message.from_user.id)
    print(user)
    if len(context.args) == 0:
        if user.status == 'admin':
            user.status = 'student'
            user.save()
            text = "Вы изменили ваш статус на student."
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        else:
            end_conversation_chat(update, context)

    else:
        if context.args[0] == ADMIN_PASSWORD:
            user.status = 'admin'
            user.save()
            text = "Вы изменили ваш статус на admin. Введите /adminhelp для просмотра списка доступных комманд"
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)

        else:
            end_conversation_chat(update, context)


@checkuser
@checkadmin
def adminhelp(update, context):
    user = User.get(id=update.message.from_user.id)
    print(user)
    if user:
        if user.status == 'admin':
            text = '<b>Список комманд:</b>\n' \
                   '● <code>/admin</code> - переключение между статусами пользователя/админа\n' \
                   '● <code>/register номер_группы пароль</code> - подключить группу к функционалу бота, ' \
                   'где <b><i>номер_группы</i></b> и <b><i>пароль</i></b> надо записать через пробел \n' \
                   '<b>ВНИМАНИЕ!</b> номер добавленной группы будет автоматически присвоен вам\n\n' \
                   '● <code>/add_task</code> - добавить новое задание\n' \
                   '● <code>/add_lecture</code> - добавить запись лекции\n' \
                   '● <code>/add_checkpoint</code> - добавить КТ\n' \
                   '● <code>/add_source</code> - добавить дополнительные материалы\n\n' \
                   '● <code>/cancel</code> - отменить создание записи на любом из шагов\n'
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)
        else:
            end_conversation_chat(update, context)


def cancel(update, context):
    print('Conversation canceled')
    text = 'Создание отменено'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)

    return ConversationHandler.END


@checkuser
@checkadmin
def add_group(update, context):
    groups = Group.select()
    numbers = [group.number for group in groups]
    user = User.get(id=update.message.from_user.id)

    if len(context.args) != 0:
        if is_number(context.args[0]):
            if int(context.args[0]) in numbers:
                text = 'Группа уже зарегистрирована'
            else:
                try:
                    prev_group = groups[-1]
                    id = prev_group.id + 1
                except Exception:
                    id = 1
                new_group = Group.create(
                    id=id,
                    number=int(context.args[0]),
                    password=context.args[1]
                )
                new_group.save()
                user.group = int(context.args[0])
                user.save()
                text = f'Группа {context.args[0]} успешно подключена!'
        else:
            print('group not number')
            text = 'Номер группы введен некорректно, воспользуйтесь образцом: <code>/add_group 1371 1234</code>,\n' \
                   'где вместо 1371 надо записать номер вашей группы\n' \
                   'а вместо 1234 - пароль, необходимый для регистрации'
    else:
        print('no arguments')

        text = 'Команда введена неверно, воспользуйтесь образцом: <code>/add_group 1371 1234</code>,\n' \
               'где вместо 1371 надо записать номер вашей группы\n' \
               'а вместо 1234 - пароль, необходимый для регистрации'
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             parse_mode=ParseMode.HTML
                             )


def add_task(update, context):
    user = User.get(id=update.message.from_user.id)
    print(user)
    if user.status == 'admin':
        context.user_data['group'] = user.group
        context.user_data['state'] = 1
        context.bot.send_message(chat_id=update.effective_chat.id, text='Введите предмет',
                                 parse_mode=telegram.ParseMode.HTML)
        return 0
    else:
        end_conversation_chat(update, context)
        return ConversationHandler.END


def task_lesson(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    context.user_data['lesson'] = update.message.text

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Введите формулировку задания (ссылку на материалы)',
                             parse_mode=telegram.ParseMode.HTML)

    context.user_data['state'] = 2
    return 1


def task_value(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    context.user_data['value'] = update.message.text

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Введите дату сдачи работы в формате (Y-m-d) Например: 2022-5-17',
                             parse_mode=telegram.ParseMode.HTML)

    tasks = Item.select().where(Item.type == types[1])
    for task in tasks:
        print(task)
    if len(tasks) > 0:
        old_task = tasks[-1]
        id = old_task.id + 1
    else:
        id = 1
    context.user_data['id'] = id

    context.user_data['state'] = 3
    return 2


def finish_task(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    try:
        date = datetime.strptime(update.message.text, '%Y-%m-%d')
    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Дата введена неверно, попробуйте еще раз!',
                                 parse_mode=ParseMode.HTML)
        context.user_data['state'] = 3
        return 2

    group = int(context.user_data['group'])
    id = int(context.user_data['id'])

    new_task = Item.create(
        id=id,
        lesson=context.user_data['lesson'],
        value=context.user_data['value'],
        group=group,
        date=date,
        type=types[1]
    )
    new_task.save()
    print('New task: ', new_task)
    text = get_item(new_task)

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)

    group_s = User.select().where(User.group == context.user_data['group'])
    for student in group_s:
        print(student)
        if student.notifications == 1:
            context.bot.send_message(
                chat_id=student.id,
                text=f"<b>Задано новое дз!</b>\n" + get_item(new_task),
                parse_mode=telegram.ParseMode.HTML
            )

    context.user_data.clear()

    return ConversationHandler.END


def add_lecture(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    user = User.get(id=update.message.from_user.id)
    if user.status == 'admin':
        context.user_data['group'] = user.group
        context.user_data['state'] = 1
        context.bot.send_message(chat_id=update.effective_chat.id, text='Введите предмет',
                                 parse_mode=telegram.ParseMode.HTML)
        print(0)
        return 0

    else:
        end_conversation_chat(update, context)
        return ConversationHandler.END


def lecture_lesson(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    context.user_data['lesson'] = update.message.text

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Введите дату проведения лекции в формате (Y-m-d) Например: 2022-5-17',
                             parse_mode=telegram.ParseMode.HTML)

    context.user_data['state'] = 2
    print(1)
    return 1


def lecture_date(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    try:
        date = datetime.strptime(update.message.text, '%Y-%m-%d')
    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Дата введена неверно, попробуйте еще раз!',
                                 parse_mode=ParseMode.HTML)
        context.user_data['state'] = 3
        return 1

    context.user_data['date'] = date

    context.bot.send_message(chat_id=update.effective_chat.id, text='Введите ссылку на материалы лекции',
                             parse_mode=telegram.ParseMode.HTML)
    return 2


def lecture_value(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    context.user_data['value'] = update.message.text
    number = 1

    lectures = Item.select().where(Item.type == types[2])
    for lecture in lectures:
        if lecture.lesson == context.user_data['lesson']:
            number = int(lecture.number) + 1
    if len(lectures) > 0:
        old_task = lectures[-1]
        id = old_task.id + 1

    else:
        number = 1
        id = 1

    group = int(context.user_data['group'])

    new_lecture = Item.create(
        id=id,
        lesson=context.user_data['lesson'],
        value=context.user_data['value'],
        group=group,
        date=context.user_data['date'],
        number=number,
        type=types[2]
    )
    new_lecture.save()
    print(new_lecture)
    text = get_item(new_lecture)

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)

    context.user_data.clear()

    return ConversationHandler.END


def add_checkpoint(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    user = User.get(id=update.message.from_user.id)
    if user.status == 'admin':
        user = User.get(id=update.message.from_user.id)
        context.user_data['group'] = user.group
        context.user_data['state'] = 1
        context.bot.send_message(chat_id=update.effective_chat.id, text='Введите предмет',
                                 parse_mode=telegram.ParseMode.HTML)
        print(0)
        return 0
    else:
        end_conversation_chat(update, context)
        return ConversationHandler.END


def checkpoint_lesson(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    context.user_data['lesson'] = update.message.text
    buttons = []

    for k in kinds.keys():
        callback_data = f'checkpoint#kind#{k}'
        buttons.append(InlineKeyboardButton(kinds[k], callback_data=callback_data))
    footer_keyboard = [InlineKeyboardButton('Отменить создание', callback_data='checkpoint#none#cancel')]
    text = 'Выберите тип: '
    reply_markup = InlineKeyboardMarkup(build_menu(buttons=buttons, n_cols=2, footer_buttons=footer_keyboard))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             parse_mode=ParseMode.HTML,
                             reply_markup=reply_markup)
    context.user_data['state'] = 2
    print(1)
    return 1


def checkpoint_kind(update, context):
    print(update)
    query = update.callback_query
    args = query.data.split('#')
    kind = ''

    if args[2] == list(kinds.keys())[0]:
        context.user_data['kind'] = 'КТ'
        kind = context.user_data['kind']
    elif args[2] == list(kinds.keys())[1]:
        context.user_data['kind'] = 'ЭКЗАМЕН'
        kind = context.user_data['kind'] + 'a'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Введите дату проведения {kind} в формате (Y-m-d) Например: 2022-5-17',
                                 parse_mode=telegram.ParseMode.HTML)
    elif args[2] == 'cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    return 2


def finish_checkpoint(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    try:
        date = datetime.strptime(update.message.text, '%Y-%m-%d')
    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Дата введена неверно, попробуйте еще раз!',
                                 parse_mode=ParseMode.HTML)
        context.user_data['state'] = 3
        return 2

    group = int(context.user_data['group'])

    checkpoints = Item.select().where(Item.type == types[3])

    if len(checkpoints) > 0:
        old_task = checkpoints[-1]
        id = old_task.id + 1

    else:
        id = 1

    new_checkpoint = Item.create(
        id=id,
        lesson=context.user_data['lesson'],
        kind=context.user_data['kind'],
        group=group,
        date=date,
        type=types[3]
    )
    new_checkpoint.save()

    print(new_checkpoint)

    text = get_item(new_checkpoint)

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)

    context.user_data.clear()
    return ConversationHandler.END


def add_source(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    user = User.get(id=update.message.from_user.id)
    if user.status == 'admin':
        sources = Item.select().where(type == types[0])
        if len(sources) > 0:
            old_source = sources[-1]
            context.user_data['id'] = old_source.id + 1

        else:
            context.user_data['id'] = 1

        context.user_data['state'] = 1
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Введите название источника, который хотите добавить',
                                 parse_mode=telegram.ParseMode.HTML)
        return 0
    else:
        end_conversation_chat(update, context)
        return ConversationHandler.END


def source_name(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    context.user_data['name'] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Введите ссылку на источник',
                             parse_mode=telegram.ParseMode.HTML)
    return 1


def finish_source(update, context):
    print(update)
    if update.message.text == '/cancel':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Создание отменено', parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    context.user_data['value'] = update.message.text

    new_source = Item.create(
        id=int(context.user_data['id']),
        lesson=context.user_data['name'],
        value=context.user_data['value'],
        type=types[0]

    )
    new_source.save()

    text = get_item(new_source)

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)

    context.user_data.clear()
    return ConversationHandler.END

from api import *
from time_work import *
from database import *
from config import *

# pip 3
import datetime
import random
import json as Json
import multitasking
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import vk_api


import os


from aiogram import Bot, Dispatcher, executor, types

from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext, filters

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
                    )
logger = logging.getLogger(__name__)


# make telegram bot
bot = Bot(token=telegram_token)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class User_Info(StatesGroup):
    user_id = ''
    user_token = State()
    group_id = State()


class answers:
    def __init__(self):
        pass

    def set_user_token(self):
        return f'Hi, to use {project_name} you must make your own account token\n' \
               '1. Go to link: https://oauth.vk.com/oauth/authorize?client_id=8035251&scope=photos,audio,video,docs,notes,pages,status,offers,questions,wall,groups,email,notifications,stats,ads,offline,docs,pages,stats,notifications&response_type=token&__q_hash=69940e59922728d45b3bca4d29ab1dc9\n' \
               '2. Copy and send address bar content'

    def token_has_been_saved(self):
        return 'Token saved successfully\nNow send please your group_id\n\n1. Go to your group\n' \
               '2. Manage -> Main Inf -> Community id\n' \
               f'Send only numbers, like {random.randrange(100000000, 999999999)}'

    def group_id_has_been_saved(self):
        return 'Group_id and user token saved\nSend your schedule or if you wont to use standard send point - .\n' \
               'Schedule format, for example [[hour, minute], [time second post], ...]'

    def error(self):
        return f'Your token-url or group id is wrong\nplease try again'

    def schudle_saved(self):
        return 'All information is collected\nNow if you send images to bot, they are put in postponed posts'

    def schedule_error(self):
        return 'Wrong schedule has wrong format\nYou can use standard schedule'

    def schedule_send(self, schedule: str):
        # [[2, 30], [7, 40], [10, 0], [14, 0], [17, 22], [20, 15]]
        time = [f"""{i[0]}: {i[1]}""" for i in schedule]
        result = ''
        for i in range(len(time)):
            result += f'Post number {i + 1} will be published at {time[i]}\n'
        return result


class tg_answers:
    def __init__(self):
        pass

    def start(self):
        return 'Hi, to use {project_name} you must make your own account token\n' \
               '1. Go to link: https://oauth.vk.com/oauth/authorize?client_id=8035251&scope=photos,audio,video,docs,notes,pages,status,offers,questions,wall,groups,email,notifications,stats,ads,offline,docs,pages,stats,notifications&response_type=token&__q_hash=69940e59922728d45b3bca4d29ab1dc9\n' \
               '2. Copy and send address bar content\n\nTo stop state write /cancel'

    def cancel(self):
        return "ok, message now won't be saved\n\nTo resume write /start"

    def set_user_token(self):
        return 'Token saved successfully\nNow send please your group_id\n\n1. Go to your group\n' \
               '2. Manage -> Main Inf -> Community id\n' \
               f'Send only numbers, like {random.randrange(100000000, 999999999)}'

    def set_group_id(self):
        return 'Your group_id has be saved\n\nNow set schedule.\nSend . - to use standard schedule\n' \
                'Or send list like that [[first post hour, first post minute],' \
               '[second post hour, second post minute], ...]' \
               '\n Or you can use keyboard upper'

    def no_user_info(self):
        return 'No info, try again'


class user_vk:
    def __init__(self, event, type):
        self.event = event
        self.type = type
        self.user_token = False

        if type is VkBotEventType.MESSAGE_NEW:
            self.event_object = event.object
            self.event_message = event.object['message']
            self.event_message_date = event.object['message']['date']
            self.event_message_from_id = event.object['message']['from_id']
            self.event_message_attachments = event.object['message']['attachments']
            self.event_message_text = event.object['message']['text']
            # self.event_message_ = event.object['message']['']

    def set_json(self, json):
        self.user_id = json['user_id']
        self.user_token = json['user_token']
        self.group_id = json['group_id']
        self.schedule = json['schedule']


@multitasking.task
def multi_task_vk():
    global get_info_vk
    flags = {}
    # dict format is like
    # {user_id: [{flag_name: 'name of flag', other variable...}, other flags...], other users...}

    print(f'vk bot work {datetime.datetime.now()}')
    vk = bot_vk(
        bot_token=bot_token,
        bot_group_id=bot_group_id
    )

    for event in vk.bot_longpool.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            # -
            # -
            user = user_vk(event, event.type)
            user_token = vk_user_inf(user_id=user.event_message_from_id)

            answer = answers()
            data = Time()
            if user.event_message_from_id in flags or not user_token:
                # if we have some flag or don't have json file
                if f"{user.event_message_from_id}" in flags.keys():
                    for flag in flags[f'{user.event_message_from_id}']:
                        # here process user flags
                        if flag['flag_name'] == 'user_token' and not flag['user_token']:
                            for i in range(len(flags[f'{user.event_message_from_id}'])):
                                if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                    flags[f'{user.event_message_from_id}'][i]['user_token'] = user.event_message_text
                            vk.send_message(user.event_message_from_id, answer.token_has_been_saved())

                        elif flag['flag_name'] == 'user_token' and not flag['group_id']:
                            for i in range(len(flags[f'{user.event_message_from_id}'])):
                                if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                    flags[f'{user.event_message_from_id}'][i]['group_id'] = user.event_message_text
                            check = user_token_and_group_id_test(flag['user_token'], user.event_message_text)
                            if check:
                                vk.send_message(user.event_message_from_id, answer.group_id_has_been_saved())

                                for i in range(len(flags[f'{user.event_message_from_id}'])):
                                    if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                        flags[f'{user.event_message_from_id}'][i][
                                            'user_token'] = check['user_token']
                            else:
                                for i in range(len(flags[f'{user.event_message_from_id}'])):
                                    if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                        none_flag = {'flag_name': 'user_token', 'user_token': False,
                                                     'group_id': False, 'schedule': False}
                                        flags[f'{user.event_message_from_id}'][i] = none_flag
                                vk.send_message(user.event_message_from_id, answer.error())

                        elif flag['flag_name'] == 'user_token' and flag['schedule'] == False:
                            for i in range(len(flags[f'{user.event_message_from_id}'])):
                                if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                    flags[f'{user.event_message_from_id}'][i]['schedule'] = user.event_message_text
                                    us, gr = flags[f'{user.event_message_from_id}'][i]['user_token'],\
                                             flags[f'{user.event_message_from_id}'][i]['group_id']

                            check = schedule_test(user.event_message_text)
                            if check:
                                json = {"user_id": user.event_message_from_id,
                                        "user_token": us,
                                        "group_id": gr,
                                        'schedule': check}
                                vk_save_user_token(user.event_message_from_id, json)
                                vk.send_message(user.event_message_from_id, answer.schudle_saved())
                                vk.send_message(user.event_message_from_id, answer.schedule_send(check))
                            else:
                                # if info user is wrong
                                for i in range(len(flags[f'{user.event_message_from_id}'])):
                                    if flags[f'{user.event_message_from_id}'][i]['flag_name'] == 'user_token':
                                        none_flag = {'flag_name': 'user_token', 'user_token': False,
                                                     'group_id': False, 'schedule': False}
                                        flags[f'{user.event_message_from_id}'][i] = none_flag
                                vk.send_message(user.event_message_from_id, answer.schedule_error())
                elif not user_token:
                    # if don't have token and you don't have flag
                    vk.send_message(user_id=user.event_message_from_id, message=f"{answer.set_user_token()}")
                    none_flag = {'flag_name': 'user_token', 'user_token': False, 'group_id': False, 'schedule': False}
                    flags[f'{user.event_message_from_id}'] = [none_flag]
            else:
                # if token file exist

                user_json = vk_user_inf(user.event_message_from_id)
                """Here write checker for json file"""
                user.set_json(user_json)
                vk_request = vk_requests(user.user_token)

                # check photo in message
                if user.event_message_attachments:
                    # here process photo(s) in message
                    photos = [i for i in user.event_message_attachments if i['type'] == 'photo']
                    post_images = []
                    for photo in photos:
                        sizes = photo['photo']['sizes']
                        for i in range(len(sizes) - 1):
                            for j in range(len(sizes) - i - 1):
                                if (sizes[j]['height'] * sizes[j]['width']) > (
                                        sizes[j + 1]['height'] * sizes[j + 1]['width']):
                                    sizes[j], sizes[j + 1] = sizes[j + 1], sizes[j]
                        # sort list by size, last image is the highest quality
                        post_images.append(download_photo('vk', user.event_message_from_id, sizes[-1]))

                    # get last post time in unixtime format
                    posts = vk_request.get_group_posts(user.group_id, count=1000,
                                                       postponed=True, last_post=True, only_time=True)
                    data.unix_time = int(posts)
                    data.datatime_convert()
                    # get the next scheduled time
                    t = vk_request.post_timetable([int(f'{data.time.hour}'), int(f'{data.time.minute}')], user.schedule)
                    if t[0]:
                        data.delta_time(delta_days=1)
                    data.replace_time(hour=t[1][0], minute=t[1][1])
                    data.unix_time_convert()
                    # make post
                    make_post = vk_request.new_post(
                        user.group_id, data.unix_time, image=post_images, text=f'{user.event_message_text}')
                    vk.send_message(user_id=user.event_message_from_id,
                                    message=f"Post redy\n{make_post}')\nTime: {data.time}\nAttachments: {post_images}")
                # here all other messages


@multitasking.task
def multi_task_telegram():
    print(f'telegram bot work {datetime.datetime.now()}')
    global ans

    ans = tg_answers()
    # executor.set_webhook(dp, 'your_server_url')
    executor.start_polling(dp)


# -------- telegram --------
@dp.message_handler(commands=['start', 'new_token'])
async def start(message: types.Message):
    await User_Info.user_token.set()
    await message.reply(ans.start())


@dp.message_handler(commands=['schedule'])
async def schedule(message: types.Message):
    u_inf = user_schedule(f"{message.from_user.id}")
    if u_inf == None:
        posts = [[InlineKeyboardButton(text="You don't have any post in schedule", callback_data='none')]]
    else:
        posts = [InlineKeyboardButton(text=f"Post {i[0]} on {i[1]}", callback_data=f'post:{i[0]}') for i in u_inf]
        if len(posts) > 3:
            po = []
            le = len(posts) // 3
            if le % 3 != 0:
                le += 1
            for i in range(le):
                po.append(posts[i * 3:(i+1)*3])
            posts = po
    keyboard = [
        [InlineKeyboardButton(text='your posts', callback_data='none')],
        *posts,
        [InlineKeyboardButton(text='make new post', callback_data='new_post')]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.reply(ans.set_group_id(), reply_markup=reply_markup)


@dp.message_handler(content_types=['photo'])
async def image(message: types.Message):
    inf = tg_user_inf(message.from_user.id)
    if inf:
        photo = message.photo[-1]
        db = Database(f'database/telegram', 'database.db')
        num = db.next_image_number(db.photo_database(message.from_user.id))
        path = os.path.join(f"database", f"telegram", f"{message.from_user.id}", f"image%{num}.png")
        file_info = await bot.get_file(photo.file_id)
        new_photo = (await bot.download_file(file_info.file_path)).read()
        with open(path, 'wb') as f:
            f.write(new_photo)

        vk_request = vk_requests(inf['user_token'])
        data = Time()
        # get last post time in unixtime format
        posts = vk_request.get_group_posts(inf['group_id'], count=1000,
                                           postponed=True, last_post=True, only_time=True)
        data.unix_time = int(posts)
        data.datatime_convert()
        # get the next scheduled time
        t = vk_request.post_timetable([int(f'{data.time.hour}'), int(f'{data.time.minute}')], inf['schedule'])
        if t[0]:
            data.delta_time(delta_days=1)
        data.replace_time(hour=t[1][0], minute=t[1][1])
        data.unix_time_convert()

        if message.text == None or message.text == 'none':
            msg_text = ''
        else:
            msg_text = message.text
        # make post
        make_post = vk_request.new_post(
            inf['group_id'], data.unix_time, image=path, text=f'{msg_text}')
        await message.answer(f"Post redy\n{make_post}')\nTime: {data.time}\nAttachments: {path}")
    else:
        await message.answer(ans.no_user_info())


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(filters.Text(equals='cancel', ignore_case=True), state='*')
async def cancel_save_message(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return None

    await state.finish()
    await message.reply(ans.cancel())


@dp.message_handler(state=User_Info.user_token)
async def set_user_token(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_token'] = message.text
    await User_Info.next()
    await message.reply(ans.set_user_token())


@dp.message_handler(state=User_Info.group_id)
async def set_group_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        check = user_token_and_group_id_test(data['user_token'], message.text)
        if check:
            data['group_id'] = check['group_id']
    if check:
        tg_save_user_token(str(message.from_user.id), {"user_id": message.from_user.id,
                                               "user_token": check['user_token'],
                                               "group_id": check['group_id']})
        await schedule(message)
    else:
        await User_Info.user_token.set()
        await message.reply('Group_id or user_token is wrong try again\n\nif you wont instruction again print /start')


@dp.callback_query_handler(text='new_post')
async def new_post(update: types.update):
    u_inf = user_schedule(update['from'].id)
    if u_inf == None:
        post_num = 1
    else:
        post_num = max([int(i[0]) for i in u_inf]) + 1
    keyboard = [
        [InlineKeyboardButton(text=f'Post number: {post_num}', callback_data='none')],
        [InlineKeyboardButton(text='<<', callback_data='--'), InlineKeyboardButton(text='<', callback_data='-'), InlineKeyboardButton(text=f'Hour: 0', callback_data='none'), InlineKeyboardButton(text='>', callback_data='+'), InlineKeyboardButton(text='>>', callback_data='++')],
        [InlineKeyboardButton(text='save hour', callback_data='save_hour')]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                                text=update.message.text, reply_markup=reply_markup)


@dp.callback_query_handler(text='save_hour')
async def save_hour(update: types.update):
    keyboard = update.message.reply_markup.inline_keyboard
    if not ' on ' in keyboard[0][0].text:
        keyboard[0][0] = InlineKeyboardButton(text=f'{keyboard[0][0].text} on {keyboard[1][2].text.split(" ")[1]}:0', callback_data='hour')
        keyboard[1][2] = InlineKeyboardButton(text=f'Min: 0', callback_data='none')
        keyboard[2][0] = InlineKeyboardButton(text=f'save minute', callback_data='save_minute')
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                                    text=update.message.text, reply_markup=reply_markup)


@dp.callback_query_handler(text='save_minute')
async def save_minute(update: types.update):
    keyboard = update.message.reply_markup.inline_keyboard
    inf = user_schedule(update['from'].id)
    if not inf:
        inf = 1
    else:
        inf = max([int(i[0]) for i in inf]) + 1
    user_schedule_add(update['from'].id, [inf, f"""{keyboard[0][0].text.split(' on ')[-1].split(':')[0]}:{keyboard[1][2].text.split('Min: ')[-1]}"""])


    u_inf = user_schedule(update['from'].id)
    if u_inf == None:
        posts = [[InlineKeyboardButton(text="You don't have any post in schedule", callback_data='none')]]
    else:
        posts = [InlineKeyboardButton(text=f"Post {i[0]} on {i[1]}", callback_data=f'post:{i[0]}') for i in u_inf]
        if len(posts) > 3:
            po = []
            le = len(posts) // 3
            if le % 3 != 0:
                le += 1
            for i in range(le):
                po.append(posts[i * 3:(i+1)*3])
            posts = po
        else:
            posts = [posts]
    keyboard = [
        [InlineKeyboardButton(text='your posts', callback_data='none')],
        *posts,
        [InlineKeyboardButton(text='make new post', callback_data='new_post')]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                                text=update.message.text, reply_markup=reply_markup)


@dp.callback_query_handler(text='+')
async def plus(update: types.update):
    # take info about third button in second line ([1][2])
    inf = (update.message.reply_markup.inline_keyboard[1][2].text.split(' '))
    if inf[0] == 'Hour:':

        hour = int(inf[1])
        if hour == 23:
            hour = 0
        elif 0 <= hour < 23:
            hour += 1
        else:
            hour = 0
        keyboard = update.message.reply_markup.inline_keyboard
        keyboard[1][2] = InlineKeyboardButton(text=f'Hour: {hour}', callback_data='hour')
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                              text=update.message.text, reply_markup=reply_markup)
    if inf[0] == 'Min:':
        hour = int(inf[1])
        if hour == 59:
            hour = 0
        elif 0 <= hour < 59:
            hour += 1
        else:
            hour = 0
        keyboard = update.message.reply_markup.inline_keyboard
        keyboard[1][2] = InlineKeyboardButton(text=f'Min: {hour}', callback_data='hour')
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                                    text=update.message.text, reply_markup=reply_markup)


@dp.callback_query_handler(text='++')
async def plusplus(update: types.update):
    # take info about third button in second line ([1][2])
    inf = (update.message.reply_markup.inline_keyboard[1][2].text.split(' '))
    if inf[0] == 'Hour:':

        hour = int(inf[1])
        if hour >= 14:
            hour -= 14
        elif 0 <= hour < 14:
            hour += 10
        else:
            hour = 0
        keyboard = update.message.reply_markup.inline_keyboard
        keyboard[1][2] = InlineKeyboardButton(text=f'Hour: {hour}', callback_data='hour')
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                                    text=update.message.text, reply_markup=reply_markup)
    if inf[0] == 'Min:':
        hour = int(inf[1])
        if hour >= 50:
            hour -= 50
        elif 0 <= hour < 50:
            hour += 10
        else:
            hour = 0
        keyboard = update.message.reply_markup.inline_keyboard
        keyboard[1][2] = InlineKeyboardButton(text=f'Min: {hour}', callback_data='hour')
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                                    text=update.message.text, reply_markup=reply_markup)


@dp.callback_query_handler(text='-')
async def minus(update: types.update):
    # take info about third button in second line ([1][2])
    inf = (update.message.reply_markup.inline_keyboard[1][2].text.split(' '))
    if inf[0] == 'Hour:':

        hour = int(inf[1])
        if hour == 0:
            hour = 23
        elif 0 < hour <= 23:
            hour -= 1
        else:
            hour = 0
        keyboard = update.message.reply_markup.inline_keyboard
        keyboard[1][2] = InlineKeyboardButton(text=f'Hour: {hour}', callback_data='hour')
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                              text=update.message.text, reply_markup=reply_markup)
    if inf[0] == 'Min:':
        hour = int(inf[1])
        if hour == 0:
            hour = 59
        elif 0 < hour <= 59:
            hour -= 1
        else:
            hour = 0
        keyboard = update.message.reply_markup.inline_keyboard
        keyboard[1][2] = InlineKeyboardButton(text=f'Min: {hour}', callback_data='hour')
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                                    text=update.message.text, reply_markup=reply_markup)


@dp.callback_query_handler(text='--')
async def minusminus(update: types.update):
    # take info about third button in second line ([1][2])
    inf = (update.message.reply_markup.inline_keyboard[1][2].text.split(' '))
    if inf[0] == 'Hour:':

        hour = int(inf[1])
        if hour <= 9:
            hour += 14
        elif 9 < hour <= 23:
            hour -= 10
        else:
            hour = 0
        keyboard = update.message.reply_markup.inline_keyboard
        keyboard[1][2] = InlineKeyboardButton(text=f'Hour: {hour}', callback_data='hour')
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                                    text=update.message.text, reply_markup=reply_markup)
    if inf[0] == 'Min:':
        hour = int(inf[1])
        if hour <= 9:
            hour += 50
        elif 9 < hour <= 60:
            hour -= 10
        else:
            hour = 0
        keyboard = update.message.reply_markup.inline_keyboard
        keyboard[1][2] = InlineKeyboardButton(text=f'Min: {hour}', callback_data='hour')
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await bot.edit_message_text(chat_id=update.message.chat.id, message_id=update.message.message_id,
                                    text=update.message.text, reply_markup=reply_markup)


def tg_user_inf(user_id):
    tg_database = Database('database/telegram', 'database.db')
    tg_database.new_directory(f'{user_id}')
    token_json = tg_database.get_file(f'{user_id}', 'token.json')

    sql = tg_database.get_from_table(f'u_{user_id}_schedule')
    if not token_json or not sql:
        return False
    else:
        schedule = [[int(j) for j in i[1].split(':')] for i in sql]
        jsn = tg_database.read_json(user_id, token_json)

        if type(schedule) is list and all([True for i in schedule if type(i) is list and len(i) == 2]) \
                and all([True for i in schedule if i[0] is list and i[1] is list]) and\
                all([(True if i in jsn.keys() else False) for i in ['user_id', 'user_token', 'group_id']]):
            jsn['schedule'] = schedule
            return jsn


def tg_save_user_token(user_id, json):
    tg_database = Database('database/telegram', 'database.db')
    tg_database.new_directory(f'{user_id}')
    tg_database.sql_user_token_table(json["user_id"], json['user_token'])
    return tg_database.save_json(user_id, json, 'token.json')


def user_schedule(user_id):
    tg_database = Database('database/telegram', 'database.db')
    if tg_database.sql_create_table(f"u_{user_id}_schedule", ['post', 'time']):
        return None
    else:
        info = tg_database.get_from_table(f'u_{user_id}_schedule')
        if not info:
            return None
        else:
            # sort by time
            items = [[int(j) for j in i[1].split(':')] for i in info]
            for i in range(len(info) - 1):
                for j in range(len(info) - i - 1):
                    if items[j][0] > items[j+1][0]:
                        info[j], info[j+1] = info[j+1], info[j]
                    elif items[j][0] == items[j+1][0]:
                        if items[j][1] > items[j + 1][1]:
                            info[j], info[j + 1] = info[j + 1], info[j]
            return info
# -------- telegram --------


def download_photo(serv, user_id, size):
    url = size['url']

    db = Database(f'database/{serv}', 'database.db')
    num = db.next_image_number(db.photo_database(user_id))
    photo = db.download_photo(user_id, url, f'image%{num}.png')
    return photo


def vk_save_user_token(user_id, json):
    vk_database = Database('database/vk', 'database.db')
    vk_database.new_directory(f'{user_id}')
    vk_database.sql_user_token_table(json["user_id"], json['user_token'])
    return (vk_database.save_json(user_id, json, 'token.json'))


def vk_user_inf(user_id):
    vk_database = Database('database/vk', 'database.db')
    vk_database.new_directory(f'{user_id}')
    token_json = vk_database.get_file(f'{user_id}', 'token.json')
    if not token_json:
        return False
    else:
        return vk_database.read_json(user_id, token_json)


def user_token_and_group_id_test(url: str, group_id: int):
    if 'com' in url or 'access_token' in url:
        url = url.split('#')
        variables = url[-1].split('&')
        variables = {f"{j[0]}": j[1] for j in [i.split('=') for i in variables]}
        token = variables["access_token"]
    else:
        token = url
    try:
        # using here normal construction with vk.API(vk.Session(access_token), v=version, lang='ru', timeout=10
        # ).secure.checkToken(token=access_token, access_token=service_token)
        vk_api.VkApi(token=token).get_api().wall.get(**{"owner_id": f'-{group_id}', "count": f'100'})
        return {'user_token': token, 'group_id': group_id}
    except:
        return False


def schedule_test(schedule: str):
    if schedule == '.':
        return schedule_table
    else:
        try:
            result = Json.loads(schedule)
            if type(result) is list and all([True for i in result if type(i) is list and len(i) == 2])\
                    and all([True for i in result if i[0] is list and i[1] is list]):
                return result
        except:
            return False


if __name__ == '__main__':
    reset = True
    while True:
        if reset:
            try:
                reset = False
                multi_task_telegram()
                multi_task_vk()
            except:
                reset = True

"""
Must make later
1) upload and download json in vk bot
2) change schedule
"""

# ---------- IMPORTS ------------

import sys

sys.path.append("..")

import telebot
import requests as rq
import sqlalchemy as sa

from io import BytesIO

from localization import ru_ru
from market_utils import getDataByYandexID
from model_utils import prepare_data, dummy_model
from sql_utils import pg_conn_string, execute_sql_safe

from model.model4 import get_gifts

# ---------- VARIABLES ----------

DEBUG = True
LOCALE = ru_ru
PROXY = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}
TELEGRAM_API_TOKEN = '1188075804:AAE9bnnSHpkCf6Pu00SZuxNxDt1pxIphTWQ'
PG_ENGINE = sa.create_engine(pg_conn_string)

# ---------- FUNCTIONS ----------


def get_insert_command(chat_id, user_reaction, model, category):
    global STATE
    sex = {LOCALE["btn_sex_male"]: 'M', LOCALE["btn_sex_female"]: 'F'}
    reason = {
        LOCALE["btn_reason_any"]: 'other',
        LOCALE["btn_reason_newYear"]: 'new_year',
        LOCALE["btn_reason_gender"]: 'gender',
        LOCALE["btn_reason_birthday"]: 'birthday'
    }

    _userState = STATE[chat_id]
    return "INSERT INTO chatbot.dbo.user_reactions (telegram_id,telegram_username,telegram_first_name," + \
           "telegram_last_name,telegram_language_code,recipient_sex,recipient_age,recipient_status," + \
           "recipient_hobby,recipient_max_cost,recipient_reason,suggestion_model_id,suggestion_category_id," + \
           "user_reaction) VALUES (" + \
           str(_userState['user_id']) + "," + \
           f"'{_userState['user_username']}'" + "," + \
           (f"'{_userState['user_first_name']}'" if _userState['user_first_name'] is not None else "NULL") + "," + \
           (f"'{_userState['user_last_name']}'" if _userState['user_last_name'] is not None else "NULL") + "," + \
           (f"'{_userState['user_language_code']}'" if _userState['user_language_code'] is not None else "NULL") + "," + \
           f"'{sex[_userState['recipient_sex']]}'" + "," + \
           str(_userState['recipient_age']) + "," + \
           f"'{_userState['recipient_status']}'" + "," + \
           "'{" + ','.join(_userState['recipient_hobby']) + "}'," + \
           f"'{_userState['recipient_cost']}'" + "," + \
           f"'{reason[_userState['recipient_reason']]}'" + "," + \
           str(model) + "," + \
           str(category) + "," + \
           f"'{user_reaction}'" + ");"


def show_menu(message):
    global STATE

    _currentChatID = message.chat.id

    _flagAllNone = (
            (STATE[_currentChatID]['recipient_sex'] is None) and
            (STATE[_currentChatID]['recipient_age'] is None) and
            (STATE[_currentChatID]['recipient_status'] is None) and
            (not STATE[_currentChatID]['recipient_hobby']) and
            (STATE[_currentChatID]['recipient_cost'] is None) and
            (STATE[_currentChatID]['recipient_reason'] is None)
    )
    _flagAllNotNone = (
            (STATE[_currentChatID]['recipient_sex'] is not None) and
            (STATE[_currentChatID]['recipient_age'] is not None) and
            (STATE[_currentChatID]['recipient_status'] is not None) and
            (STATE[_currentChatID]['recipient_hobby']) and
            (STATE[_currentChatID]['recipient_cost'] is not None) and
            (STATE[_currentChatID]['recipient_reason'] is not None)
    )
    if _flagAllNotNone:
        sex = {LOCALE["btn_sex_male"]: 'M', LOCALE["btn_sex_female"]: 'F'}
        reason = {
            LOCALE["btn_reason_any"]: 'other',
            LOCALE["btn_reason_newYear"]: 'new_year',
            LOCALE["btn_reason_gender"]: 'gender',
            LOCALE["btn_reason_birthday"]: 'birthday'
        }
        bot.send_message(_currentChatID, LOCALE["msg_loading"])
        if DEBUG:
            bot.send_message(
                _currentChatID,
                f"```\n------ DEBUG -----\n"
                f"------------------\n"
                f"Passing data into model\n"
                f"• sex\t{sex[STATE[_currentChatID]['recipient_sex']]}\n"
                f"• age\t{STATE[_currentChatID]['recipient_age']}\n"
                f"• status\t{STATE[_currentChatID]['recipient_status']}\n"
                f"• hobby\t{','.join(STATE[_currentChatID]['recipient_hobby'])}\n"
                f"• max_price\t{STATE[_currentChatID]['recipient_cost']}\n"
                f"• reason\t{reason[STATE[_currentChatID]['recipient_reason']]}```",
                parse_mode='markdown'
            )
        STATE[_currentChatID]['suggestion_goods'] = get_gifts(
            prepare_data(
                sex[STATE[_currentChatID]['recipient_sex']],
                STATE[_currentChatID]['recipient_age'],
                STATE[_currentChatID]['recipient_status'],
                ','.join(STATE[_currentChatID]['recipient_hobby']),
                STATE[_currentChatID]['recipient_reason']
            ), max_cost=STATE[_currentChatID]['recipient_cost'], min_cost=0
        )
        message = bot.send_message(_currentChatID, LOCALE["msg_ready"])
        if DEBUG:
            bot.send_message(
                _currentChatID,
                f"```\n------ DEBUG -----\n"
                f"------------------\n"
                f"{STATE[_currentChatID]['suggestion_goods']}```",
                parse_mode='markdown')
        show_suggestion(message)
    else:
        _keyboard = telebot.types.InlineKeyboardMarkup()
        if STATE[_currentChatID]['recipient_sex'] is None:
            _keySex = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_sex'], callback_data='sex')
            _keyboard.add(_keySex)
        if STATE[_currentChatID]['recipient_age'] is None:
            _keyAge = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_age'], callback_data='age')
            _keyboard.add(_keyAge)
        if STATE[_currentChatID]['recipient_status'] is None:
            _keyStatus = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_status'], callback_data='status')
            _keyboard.add(_keyStatus)
        if not STATE[_currentChatID]['recipient_hobby']:
            _keyHobby = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_hobby'], callback_data='hobby')
            _keyboard.add(_keyHobby)
        if STATE[_currentChatID]['recipient_cost'] is None:
            _keyCost = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_cost'], callback_data='cost')
            _keyboard.add(_keyCost)
        if STATE[_currentChatID]['recipient_reason'] is None:
            _keyReason = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_reason'], callback_data='reason')
            _keyboard.add(_keyReason)
        _keyBack = telebot.types.InlineKeyboardButton(text=LOCALE['btn_back'], callback_data='back')
        _keyboard.add(_keyBack)
        bot.send_message(
            _currentChatID,
            (
                    (LOCALE['msg_getData_body'] if _flagAllNone else LOCALE['msg_getData_body_mid']) +
                    (
                        f"⏳ {LOCALE['msg_getData_sex']}\n"
                        if STATE[_currentChatID]['recipient_sex'] is None
                        else f"✅ {LOCALE['msg_getData_sex']} - {STATE[_currentChatID]['recipient_sex']}\n"
                    ) + (
                        f"⏳ {LOCALE['msg_getData_age']}\n"
                        if STATE[_currentChatID]['recipient_age'] is None
                        else f"✅ {LOCALE['msg_getData_age']} - {STATE[_currentChatID]['recipient_age']}\n"
                    ) + (
                        f"⏳ {LOCALE['msg_getData_status']}\n"
                        if STATE[_currentChatID]['recipient_status'] is None
                        else f"✅ {LOCALE['msg_getData_status']} - {STATE[_currentChatID]['recipient_status']}\n"
                    ) + (
                        f"⏳ {LOCALE['msg_getData_hobby']}\n"
                        if STATE[_currentChatID]['recipient_hobby'] == []
                        else f"✅ {LOCALE['msg_getData_hobby']} - {', '.join(STATE[_currentChatID]['recipient_hobby'])}\n"
                    ) + (
                        f"⏳ {LOCALE['msg_getData_cost']}\n"
                        if STATE[_currentChatID]['recipient_cost'] is None
                        else f"✅ {LOCALE['msg_getData_cost']} - {STATE[_currentChatID]['recipient_cost']}₽\n"
                    ) + (
                        f"⏳ {LOCALE['msg_getData_reason']}\n"
                        if STATE[_currentChatID]['recipient_reason'] is None
                        else f"✅ {LOCALE['msg_getData_reason']} - {STATE[_currentChatID]['recipient_reason']}\n"
                    ) + (LOCALE['msg_getData_footer'])
            ),
            reply_markup=_keyboard
        )


def show_suggestion(message):
    global STATE

    _currentChatID = message.chat.id
    STATE[_currentChatID]['suggestion_keyboard'] = []

    _suggestedItem = getDataByYandexID(
        STATE[_currentChatID]['suggestion_goods'][
            STATE[_currentChatID]['suggestion_current']
        ]['model'])

    _tmpImage = BytesIO(
        rq.get(
            url=_suggestedItem['photo'],
            headers={
                'authority': 'avatars.mds.yandex.net',
                'user-agent': 'Market/1172 CFNetwork/1121.2.2 Darwin/19.3.0',
                'accept': '*/*',
                'accept-language': 'en-us',
                'accept-encoding': 'gzip, deflate, br'
            }
        ).content
    )
    _tmpImageMsg = bot.send_photo(_currentChatID, _tmpImage)

    _keyboard = telebot.types.InlineKeyboardMarkup()
    _keyMarket = telebot.types.InlineKeyboardButton(
        text=LOCALE['btn_get_market'],
        callback_data='goto_market'
    )
    _keyboard.add(_keyMarket)
    _keyGet = telebot.types.InlineKeyboardButton(
        text=LOCALE['btn_get_link'],
        callback_data='goto_shop'
    )
    _keyboard.add(_keyGet)
    _keyNext = telebot.types.InlineKeyboardButton(
        text=LOCALE['btn_get_next'],
        callback_data='try_another'
    )
    _keyboard.add(_keyNext)
    _keyNew = telebot.types.InlineKeyboardButton(
        text=LOCALE['btn_new_gift'],
        callback_data='new_gift'
    )
    _keyboard.add(_keyNew)
    bot.send_message(
        message.chat.id,
        f"_Информация предоставлена сервисом Яндекс.Маркет_\n\n"
        f"*{_suggestedItem['name']}*\n"
        f"{_suggestedItem['description']}\n\n"
        f"_B соответствии с пунктом 6.2 [пользовательского соглашения сервисов Яндекса](https://yandex.ru/legal/rules/)"
        f" мы используем контент сервиса Яндекс.Маркет исключительно для личного некоммерческого использования с "
        f"сохранением всех знаков охраны авторского права, смежных прав, товарных знаков, других уведомлений об "
        f"авторстве, сохранения имени (или псевдонима) автора/наименования правообладателя в неизменном виде. Все "
        f"данные, полученные в ходе выполнения данной курсовой работы, предназначены для личного некоммерческого "
        f"использования и исключительно в целях демонстрации возможности существования подобного сервиса. Мы "
        f"уважаем работу, проделанную командой сервиса Яндекс.Маркет, и не стремимся ущемить их исключительное "
        f"право на весь контент, предоставляемый сервисом_",
        parse_mode='markdown',
        reply_to_message_id=_tmpImageMsg.message_id,
        reply_markup=_keyboard
    )

    STATE[_currentChatID]['suggestion_keyboard'].append(_keyMarket)
    STATE[_currentChatID]['suggestion_keyboard'].append(_keyGet)
    STATE[_currentChatID]['suggestion_keyboard'].append(_keyNext)
    STATE[_currentChatID]['suggestion_keyboard'].append(_keyNew)


# ---------- CODE ---------------

telebot.apihelper.proxy = PROXY
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

STATE = {}


@bot.message_handler(commands=['start'])
def start_handler(message):

    global STATE
    _currentChatID = message.chat.id
    STATE[_currentChatID] = {}
    STATE[_currentChatID]['user_id'] = message.from_user.id
    STATE[_currentChatID]['user_username'] = message.from_user.username
    STATE[_currentChatID]['user_first_name'] = message.from_user.first_name
    STATE[_currentChatID]['user_last_name'] = message.from_user.last_name
    STATE[_currentChatID]['user_language_code'] = message.from_user.language_code
    # ---
    STATE[_currentChatID]['recipient_sex'] = None
    STATE[_currentChatID]['recipient_age'] = None
    STATE[_currentChatID]['recipient_status'] = None
    STATE[_currentChatID]['recipient_hobby'] = []
    STATE[_currentChatID]['recipient_cost'] = None
    STATE[_currentChatID]['recipient_reason'] = None
    # ---
    STATE[_currentChatID]['suggestion_goods'] = []
    STATE[_currentChatID]['suggestion_current'] = 0
    STATE[_currentChatID]['suggestion_keyboard'] = []
    # ---
    STATE[_currentChatID]['current_stage'] = '1_start'

    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row(LOCALE['btn_start'])
    keyboard.row(LOCALE['btn_about'])

    bot.send_message(message.chat.id, LOCALE['msg_start'], reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def text_handler(message):
    global STATE

    _currentChatID = message.chat.id
    _currentUserStage = STATE[_currentChatID]['current_stage']

    if _currentUserStage == '1_start' and message.text.lower() == LOCALE['btn_about'].lower():
        bot.send_message(message.chat.id, LOCALE['msg_about'])
    elif _currentUserStage == '1_start' and message.text.lower() == LOCALE['btn_start'].lower():
        STATE[_currentChatID]['current_stage'] = '2_input'
        show_menu(message)
    elif _currentUserStage == '2_sex':
        if message.text == LOCALE['btn_sex_male']:
            STATE[_currentChatID]['recipient_sex'] = LOCALE['btn_sex_male']
            show_menu(message)
        elif message.text == LOCALE['btn_sex_female']:
            STATE[_currentChatID]['recipient_sex'] = LOCALE['btn_sex_female']
            show_menu(message)
    elif _currentUserStage == '2_age':
        try:
            STATE[_currentChatID]['recipient_age'] = int(message.text)
            show_menu(message)
        except Exception:
            bot.send_message(_currentChatID, LOCALE["msg_getAge"])
    elif _currentUserStage == '2_status':
        if message.text == LOCALE['btn_status_random']:
            STATE[_currentChatID]['recipient_status'] = LOCALE['btn_status_random']
            show_menu(message)
        elif message.text == LOCALE['btn_status_friend']:
            STATE[_currentChatID]['recipient_status'] = LOCALE['btn_status_friend']
            show_menu(message)
        elif message.text == LOCALE['btn_status_colleague']:
            STATE[_currentChatID]['recipient_status'] = LOCALE['btn_status_colleague']
            show_menu(message)
        elif message.text == LOCALE['btn_status_date']:
            STATE[_currentChatID]['recipient_status'] = LOCALE['btn_status_date']
            show_menu(message)
        elif message.text == LOCALE['btn_status_relative']:
            STATE[_currentChatID]['recipient_status'] = LOCALE['btn_status_relative']
            show_menu(message)
    elif _currentUserStage == '2_hobby':
        if message.text == LOCALE['btn_hobby_end']:
            show_menu(message)
        elif message.text == LOCALE['btn_hobby_reading']:
            STATE[_currentChatID]['recipient_hobby'].append('чтение')
        elif message.text == LOCALE['btn_hobby_photo']:
            STATE[_currentChatID]['recipient_hobby'].append('фотография')
        elif message.text == LOCALE['btn_hobby_cook']:
            STATE[_currentChatID]['recipient_hobby'].append('кулинария')
        elif message.text == LOCALE['btn_hobby_sport']:
            STATE[_currentChatID]['recipient_hobby'].append('спорт')
        elif message.text == LOCALE['btn_hobby_travel']:
            STATE[_currentChatID]['recipient_hobby'].append('путешествия')
        elif message.text == LOCALE['btn_hobby_board']:
            STATE[_currentChatID]['recipient_hobby'].append('настольные игры')
        elif message.text == LOCALE['btn_hobby_movie']:
            STATE[_currentChatID]['recipient_hobby'].append('кино')
        elif message.text == LOCALE['btn_hobby_music']:
            STATE[_currentChatID]['recipient_hobby'].append('музыка')
        elif message.text == LOCALE['btn_hobby_games']:
            STATE[_currentChatID]['recipient_hobby'].append('видеоигры')
        elif message.text == LOCALE['btn_hobby_art']:
            STATE[_currentChatID]['recipient_hobby'].append('искусство')
        elif message.text == LOCALE['btn_hobby_it']:
            STATE[_currentChatID]['recipient_hobby'].append('IT')
        elif message.text == LOCALE['btn_hobby_garden']:
            STATE[_currentChatID]['recipient_hobby'].append('садоводство')
        elif message.text == LOCALE['btn_hobby_craft']:
            STATE[_currentChatID]['recipient_hobby'].append('рукоделие')
        else:
            STATE[_currentChatID]['recipient_hobby'].extend([i.lower() for i in message.text.split(',')])
    elif _currentUserStage == '2_cost':
        try:
            STATE[_currentChatID]['recipient_cost'] = int(message.text)
            show_menu(message)
        except Exception:
            bot.send_message(message.from_user.id, LOCALE["msg_getCost"])
    elif _currentUserStage == '2_reason':
        if message.text == LOCALE['btn_reason_any']:
            STATE[_currentChatID]['recipient_reason'] = LOCALE['btn_reason_any']
            show_menu(message)
        elif message.text == LOCALE['btn_reason_newYear']:
            STATE[_currentChatID]['recipient_reason'] = LOCALE['btn_reason_newYear']
            show_menu(message)
        elif message.text == LOCALE['btn_reason_gender']:
            STATE[_currentChatID]['recipient_reason'] = LOCALE['btn_reason_gender']
            show_menu(message)
        elif message.text == LOCALE['btn_reason_birthday']:
            STATE[_currentChatID]['recipient_reason'] = LOCALE['btn_reason_birthday']
            show_menu(message)
    print(STATE)


@bot.callback_query_handler(func=lambda call: call.data in ["sex", "age", "status", "hobby", "cost", "reason", "back"])
def menu_response_handler(call):
    global STATE

    _currentChatID = call.message.chat.id

    if call.data == "sex":
        _keyboard = telebot.types.ReplyKeyboardMarkup()
        _keyboard.row(LOCALE['btn_sex_male'])
        _keyboard.row(LOCALE['btn_sex_female'])

        STATE[_currentChatID]['current_stage'] = '2_sex'
        bot.send_message(_currentChatID, LOCALE['msg_getSex'], reply_markup=_keyboard)
    elif call.data == "age":
        STATE[_currentChatID]['current_stage'] = '2_age'
        bot.send_message(_currentChatID, LOCALE["msg_getAge"])
    elif call.data == "status":
        _keyboard = telebot.types.ReplyKeyboardMarkup()
        _keyboard.row(LOCALE['btn_status_random'])
        _keyboard.row(LOCALE['btn_status_friend'])
        _keyboard.row(LOCALE['btn_status_colleague'])
        _keyboard.row(LOCALE['btn_status_date'])
        _keyboard.row(LOCALE['btn_status_relative'])

        STATE[_currentChatID]['current_stage'] = '2_status'
        bot.send_message(_currentChatID, LOCALE['msg_getStatus'], reply_markup=_keyboard)
    elif call.data == "hobby":
        _keyboard = telebot.types.ReplyKeyboardMarkup()
        _keyboard.row(LOCALE['btn_hobby_end'])
        _keyboard.row(LOCALE['btn_hobby_reading'], LOCALE['btn_hobby_photo'])
        _keyboard.row(LOCALE['btn_hobby_cook'], LOCALE['btn_hobby_sport'])
        _keyboard.row(LOCALE['btn_hobby_travel'], LOCALE['btn_hobby_board'])
        _keyboard.row(LOCALE['btn_hobby_movie'], LOCALE['btn_hobby_music'])
        _keyboard.row(LOCALE['btn_hobby_games'], LOCALE['btn_hobby_art'])
        _keyboard.row(LOCALE['btn_hobby_it'], LOCALE['btn_hobby_garden'])
        _keyboard.row(LOCALE['btn_hobby_craft'])

        STATE[_currentChatID]['current_stage'] = '2_hobby'
        bot.send_message(_currentChatID, LOCALE['msg_getHobby'], reply_markup=_keyboard)
    elif call.data == "cost":
        STATE[_currentChatID]['current_stage'] = '2_cost'
        bot.send_message(_currentChatID, LOCALE["msg_getCost"])
    elif call.data == "reason":
        _keyboard = telebot.types.ReplyKeyboardMarkup()
        _keyboard.row(LOCALE['btn_reason_any'])
        _keyboard.row(LOCALE['btn_reason_newYear'])
        _keyboard.row(LOCALE['btn_reason_gender'])
        _keyboard.row(LOCALE['btn_reason_birthday'])

        STATE[_currentChatID]['current_stage'] = '2_reason'
        bot.send_message(_currentChatID, LOCALE['msg_getReason'], reply_markup=_keyboard)
    elif call.data == "back":
        start_handler(call.message)


@bot.callback_query_handler(func=lambda call: call.data in ["goto_market", "goto_shop", "try_another", "new_gift"])
def item_response_handler(call):
    global STATE

    _currentChatID = call.message.chat.id

    if call.data == "goto_market":
        _suggestedItem = getDataByYandexID(
            STATE[_currentChatID]['suggestion_goods'][
                STATE[_currentChatID]['suggestion_current']
            ]['model'])
        _keyboard = telebot.types.InlineKeyboardMarkup()
        STATE[_currentChatID]['suggestion_keyboard'][0] = telebot.types.InlineKeyboardButton(
            text=LOCALE['btn_goto_market'],
            url=_suggestedItem['market_link']
        )
        for key in STATE[_currentChatID]['suggestion_keyboard']:
            _keyboard.add(key)
        bot.edit_message_reply_markup(
            chat_id=_currentChatID,
            message_id=call.message.message_id,
            reply_markup=_keyboard
        )
        if DEBUG:
            bot.send_message(
                call.message.chat.id,
                f"```\n------ DEBUG -----\n"
                f"------------------\n"
                f"User liked the suggestion from the bot\n"
                f"and used a link to go to Yandex.Market\n"
                f"------------------\n"
                f"Result will be recorded to PostreSQL DB\n"
                f"telegram_user_id\t{STATE[_currentChatID]['user_id']}\n"
                f"telegram_user_username\t{STATE[_currentChatID]['user_username']}\n"
                f"telegram_user_first_name\t{STATE[_currentChatID]['user_first_name']}\n"
                f"telegram_user_last_name\t{STATE[_currentChatID]['user_last_name']}\n"
                f"telegram_user_language_code\t{STATE[_currentChatID]['user_language_code']}\n```",
                parse_mode='markdown'
            )
        execute_sql_safe(
            get_insert_command(
                _currentChatID,
                'goto_market',
                STATE[_currentChatID]['suggestion_goods'][
                    STATE[_currentChatID]['suggestion_current']
                ]['model'],
                STATE[_currentChatID]['suggestion_goods'][
                    STATE[_currentChatID]['suggestion_current']
                ]['category']
            ),
            PG_ENGINE,
            f"log user info (user_id={STATE[_currentChatID]['user_id']},item_num={STATE[_currentChatID]['suggestion_current']})"
        )
    elif call.data == "goto_shop":
        _suggestedItem = getDataByYandexID(
            STATE[_currentChatID]['suggestion_goods'][
                STATE[_currentChatID]['suggestion_current']
            ]['model'])
        _keyboard = telebot.types.InlineKeyboardMarkup()
        STATE[_currentChatID]['suggestion_keyboard'][1] = telebot.types.InlineKeyboardButton(
            text=LOCALE['btn_goto_link'],
            url=_suggestedItem['best_offer']['url']
        )
        for key in STATE[_currentChatID]['suggestion_keyboard']:
            _keyboard.add(key)
        bot.edit_message_reply_markup(
            chat_id=_currentChatID,
            message_id=call.message.message_id,
            reply_markup=_keyboard
        )
        if DEBUG:
            bot.send_message(
                call.message.chat.id,
                f"```\n------ DEBUG -----\n"
                f"------------------\n"
                f"User liked the suggestion from the bot\n"
                f"and used a link to go directly to the shop\n"
                f"------------------\n"
                f"Result will be recorded to PostreSQL DB\n"
                f"telegram_user_id\t{STATE[_currentChatID]['user_id']}\n"
                f"telegram_user_username\t{STATE[_currentChatID]['user_username']}\n"
                f"telegram_user_first_name\t{STATE[_currentChatID]['user_first_name']}\n"
                f"telegram_user_last_name\t{STATE[_currentChatID]['user_last_name']}\n"
                f"telegram_user_language_code\t{STATE[_currentChatID]['user_language_code']}\n```",
                parse_mode='markdown'
            )
        execute_sql_safe(
            get_insert_command(
                _currentChatID,
                'goto_store',
                STATE[_currentChatID]['suggestion_goods'][
                    STATE[_currentChatID]['suggestion_current']
                ]['model'],
                STATE[_currentChatID]['suggestion_goods'][
                    STATE[_currentChatID]['suggestion_current']
                ]['category']
            ),
            PG_ENGINE,
            f"log user info (user_id={STATE[_currentChatID]['user_id']},item_num={STATE[_currentChatID]['suggestion_current']})"
        )
    elif call.data == "try_another":
        if DEBUG:
            bot.send_message(
                call.message.chat.id,
                f"```\n------ DEBUG -----\n"
                f"------------------\n"
                f"User didn't like the suggestion from the bot\n"
                f"and asked for another suggestion\n"
                f"------------------\n"
                f"Result will be recorded to PostreSQL DB\n"
                f"telegram_user_id\t{STATE[_currentChatID]['user_id']}\n"
                f"telegram_user_username\t{STATE[_currentChatID]['user_username']}\n"
                f"telegram_user_first_name\t{STATE[_currentChatID]['user_first_name']}\n"
                f"telegram_user_last_name\t{STATE[_currentChatID]['user_last_name']}\n"
                f"telegram_user_language_code\t{STATE[_currentChatID]['user_language_code']}\n```",
                parse_mode='markdown'
            )
        execute_sql_safe(
            get_insert_command(
                _currentChatID,
                'next_item',
                STATE[_currentChatID]['suggestion_goods'][
                    STATE[_currentChatID]['suggestion_current']
                ]['model'],
                STATE[_currentChatID]['suggestion_goods'][
                    STATE[_currentChatID]['suggestion_current']
                ]['category']
            ),
            PG_ENGINE,
            f"log user info (user_id={STATE[_currentChatID]['user_id']},item_num={STATE[_currentChatID]['suggestion_current']})"
        )
        if STATE[_currentChatID]['suggestion_current'] < len(STATE[_currentChatID]['suggestion_goods']) - 1:
            STATE[_currentChatID]['suggestion_current'] += 1
            show_suggestion(call.message)
        else:
            bot.send_message(
                call.message.chat.id,
                f"```\n------ DEBUG -----\n"
                f"------------------\n"
                f"Out of suggestions for now```",
                parse_mode='markdown'
            )
    elif call.data == "new_gift":
        start_handler(call.message)


bot.enable_save_next_step_handlers(delay=0.5)
bot.load_next_step_handlers()

bot.polling()

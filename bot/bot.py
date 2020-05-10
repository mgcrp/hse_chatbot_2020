# ---------- IMPORTS ------------
import telebot
from locale import ru_ru

# ---------- VARIABLES ----------
TELEGRAM_API_TOKEN = '1188075804:AAE9bnnSHpkCf6Pu00SZuxNxDt1pxIphTWQ'
LOCALE = ru_ru


# ---------- FUNCTIONS ----------
def send_get_menu(chat_id):
    flag_all_none = ((recipient_sex is None) and (recipient_age is None) and (recipient_status is None) and
                     (not recipient_hobby) and (recipient_cost is None) and (recipient_reason is None))
    flag_all_not_none = ((recipient_sex is not None) and (recipient_age is not None) and (recipient_status is not None)
                         and recipient_hobby and (recipient_cost is not None) and (recipient_reason is not None))

    if flag_all_not_none:
        sex = {LOCALE["btn_sex_male"]: 'M', LOCALE["btn_sex_female"]: 'F'}
        reason = {
            LOCALE["btn_reason_any"]: 'other',
            LOCALE["btn_reason_newYear"]: 'new_year',
            LOCALE["btn_reason_gender"]: 'gender',
            LOCALE["btn_reason_birthday"]: 'birthday'
        }

        bot.send_message(chat_id, 'Начинаю магию! 🧙🏻‍')
        bot.send_message(chat_id, f"""
------ DEBUG -----
------------------
Passing data into model
• sex\t{sex[recipient_sex]}
• age\t{recipient_age}
• status\t{recipient_status}
• hobby\t{','.join(recipient_hobby)}
• max_price\t{recipient_cost}
• reason\t{reason[recipient_reason]}
""")
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()
        if recipient_sex is None:
            key_sex = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_sex'], callback_data='sex')
            keyboard.add(key_sex)
        if recipient_age is None:
            key_age = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_age'], callback_data='age')
            keyboard.add(key_age)
        if recipient_status is None:
            key_status = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_status'], callback_data='status')
            keyboard.add(key_status)
        if not recipient_hobby:
            key_hobby = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_hobby'], callback_data='hobby')
            keyboard.add(key_hobby)
        if recipient_cost is None:
            key_cost = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_cost'], callback_data='cost')
            keyboard.add(key_cost)
        if recipient_reason is None:
            key_reason = telebot.types.InlineKeyboardButton(text=LOCALE['msg_getData_reason'], callback_data='reason')
            keyboard.add(key_reason)

        bot.send_message(
            chat_id,
            LOCALE['msg_getData_body'] if flag_all_none else LOCALE['msg_getData_body_mid'] +
                                                             (
                                                                 f"⏳ {LOCALE['msg_getData_sex']}\n" if recipient_sex is None else f"✅ {LOCALE['msg_getData_sex']} - {recipient_sex}\n") +
                                                             (
                                                                 f"⏳ {LOCALE['msg_getData_age']}\n" if recipient_age is None else f"✅ {LOCALE['msg_getData_age']} - {recipient_age}\n") +
                                                             (
                                                                 f"⏳ {LOCALE['msg_getData_status']}\n" if recipient_status is None else f"✅ {LOCALE['msg_getData_status']} - {recipient_status}\n") +
                                                             (
                                                                 f"⏳ {LOCALE['msg_getData_hobby']}\n" if recipient_hobby == [] else f"✅ {LOCALE['msg_getData_hobby']} - {', '.join(recipient_hobby)}\n") +
                                                             (
                                                                 f"⏳ {LOCALE['msg_getData_cost']}\n" if recipient_cost is None else f"✅ {LOCALE['msg_getData_cost']} - {recipient_cost}₽\n") +
                                                             (
                                                                 f"⏳ {LOCALE['msg_getData_reason']}\n" if recipient_reason is None else f"✅ {LOCALE['msg_getData_reason']} - {recipient_reason}\n") +
                                                             LOCALE['msg_getData_footer'],
            reply_markup=keyboard
        )


# ---------- CODE ---------------
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

recipient_sex = None
recipient_age = None
recipient_status = None
recipient_hobby = []
recipient_cost = None
recipient_reason = None


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row(LOCALE['btn_start'])
    keyboard.row(LOCALE['btn_about'])

    bot.send_message(message.chat.id, LOCALE['msg_start'], reply_markup=keyboard)
    bot.register_next_step_handler(message, start_menu_response)


@bot.message_handler(content_types=['text'])
def start_menu_response(message):
    global recipient_sex
    global recipient_age
    global recipient_status
    global recipient_hobby
    global recipient_cost
    global recipient_reason

    if message.text.lower() == LOCALE['btn_about'].lower():
        bot.send_message(message.chat.id, LOCALE['msg_about'])
    elif message.text.lower() == LOCALE['btn_start'].lower():
        recipient_sex = None
        recipient_age = None
        recipient_status = None
        recipient_hobby = []
        recipient_cost = None
        recipient_reason = None
        send_get_menu(message.chat.id)


def get_sex(message):
    global recipient_sex
    if message.text == LOCALE['btn_sex_male']:
        recipient_sex = LOCALE['btn_sex_male']
        send_get_menu(message.chat.id)
    elif message.text == LOCALE['btn_sex_female']:
        recipient_sex = LOCALE['btn_sex_female']
        send_get_menu(message.chat.id)
    else:
        bot.register_next_step_handler(message, get_sex)


def get_age(message):
    global recipient_age
    try:
        recipient_age = int(message.text)
        send_get_menu(message.chat.id)
    except Exception:
        bot.send_message(message.from_user.id, LOCALE["msg_getAge"])
        bot.register_next_step_handler(message, get_age)


def get_status(message):
    global recipient_status
    if message.text == LOCALE['btn_status_random']:
        recipient_status = LOCALE['btn_status_random']
        send_get_menu(message.chat.id)
    elif message.text == LOCALE['btn_status_friend']:
        recipient_status = LOCALE['btn_status_friend']
        send_get_menu(message.chat.id)
    elif message.text == LOCALE['btn_status_colleague']:
        recipient_status = LOCALE['btn_status_colleague']
        send_get_menu(message.chat.id)
    elif message.text == LOCALE['btn_status_date']:
        recipient_status = LOCALE['btn_status_date']
        send_get_menu(message.chat.id)
    elif message.text == LOCALE['btn_status_relative']:
        recipient_status = LOCALE['btn_status_relative']
        send_get_menu(message.chat.id)
    else:
        bot.register_next_step_handler(message, get_status)


def get_hobby(message):
    global recipient_hobby
    if message.text == LOCALE['btn_hobby_end']:
        send_get_menu(message.chat.id)
    elif message.text == LOCALE['btn_hobby_reading']:
        recipient_hobby.append('чтение')
    elif message.text == LOCALE['btn_hobby_photo']:
        recipient_hobby.append('фотография')
    elif message.text == LOCALE['btn_hobby_cook']:
        recipient_hobby.append('кулинария')
    elif message.text == LOCALE['btn_hobby_sport']:
        recipient_hobby.append('спорт')
    elif message.text == LOCALE['btn_hobby_travel']:
        recipient_hobby.append('путешествия')
    elif message.text == LOCALE['btn_hobby_board']:
        recipient_hobby.append('настольные игры')
    elif message.text == LOCALE['btn_hobby_movie']:
        recipient_hobby.append('кино')
    elif message.text == LOCALE['btn_hobby_music']:
        recipient_hobby.append('музыка')
    elif message.text == LOCALE['btn_hobby_games']:
        recipient_hobby.append('видеоигры')
    elif message.text == LOCALE['btn_hobby_art']:
        recipient_hobby.append('искусство')
    elif message.text == LOCALE['btn_hobby_it']:
        recipient_hobby.append('IT')
    elif message.text == LOCALE['btn_hobby_garden']:
        recipient_hobby.append('садоводство')
    elif message.text == LOCALE['btn_hobby_craft']:
        recipient_hobby.append('рукоделие')
    else:
        recipient_hobby.extend([i.lower() for i in message.text.split(',')])
    bot.register_next_step_handler(message, get_hobby)


def get_cost(message):
    global recipient_cost
    try:
        recipient_cost = int(message.text)
        send_get_menu(message.chat.id)
    except Exception:
        bot.send_message(message.from_user.id, LOCALE["msg_getCost"])
        bot.register_next_step_handler(message, get_cost)


def get_reason(message):
    global recipient_reason
    if message.text == LOCALE['btn_reason_any']:
        recipient_reason = LOCALE['btn_reason_any']
        send_get_menu(message.chat.id)
    elif message.text == LOCALE['btn_reason_newYear']:
        recipient_reason = LOCALE['btn_reason_newYear']
        send_get_menu(message.chat.id)
    elif message.text == LOCALE['btn_reason_gender']:
        recipient_reason = LOCALE['btn_reason_gender']
        send_get_menu(message.chat.id)
    elif message.text == LOCALE['btn_reason_birthday']:
        recipient_reason = LOCALE['btn_reason_birthday']
        send_get_menu(message.chat.id)
    else:
        bot.register_next_step_handler(message, get_reason)


@bot.callback_query_handler(func=lambda call: True)
def get_menu_response(call):
    if call.data == "sex":
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row(LOCALE['btn_sex_male'])
        keyboard.row(LOCALE['btn_sex_female'])
        answer = bot.send_message(call.message.chat.id, LOCALE['msg_getSex'], reply_markup=keyboard)
        bot.register_next_step_handler(answer, get_sex)
    elif call.data == "age":
        answer = bot.send_message(call.message.chat.id, LOCALE["msg_getAge"])
        bot.register_next_step_handler(answer, get_age)
    elif call.data == "status":
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row(LOCALE['btn_status_random'])
        keyboard.row(LOCALE['btn_status_friend'])
        keyboard.row(LOCALE['btn_status_colleague'])
        keyboard.row(LOCALE['btn_status_date'])
        keyboard.row(LOCALE['btn_status_relative'])
        answer = bot.send_message(call.message.chat.id, LOCALE['msg_getStatus'], reply_markup=keyboard)
        bot.register_next_step_handler(answer, get_status)
    elif call.data == "hobby":
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row(LOCALE['btn_hobby_end'])
        keyboard.row(LOCALE['btn_hobby_reading'], LOCALE['btn_hobby_photo'])
        keyboard.row(LOCALE['btn_hobby_cook'], LOCALE['btn_hobby_sport'])
        keyboard.row(LOCALE['btn_hobby_travel'], LOCALE['btn_hobby_board'])
        keyboard.row(LOCALE['btn_hobby_movie'], LOCALE['btn_hobby_music'])
        keyboard.row(LOCALE['btn_hobby_games'], LOCALE['btn_hobby_art'])
        keyboard.row(LOCALE['btn_hobby_it'], LOCALE['btn_hobby_garden'])
        keyboard.row(LOCALE['btn_hobby_craft'])
        answer = bot.send_message(call.message.chat.id, LOCALE['msg_getHobby'], reply_markup=keyboard)
        bot.register_next_step_handler(answer, get_hobby)
    elif call.data == "cost":
        answer = bot.send_message(call.message.chat.id, LOCALE["msg_getCost"])
        bot.register_next_step_handler(answer, get_cost)
    elif call.data == "reason":
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row(LOCALE['btn_reason_any'])
        keyboard.row(LOCALE['btn_reason_newYear'])
        keyboard.row(LOCALE['btn_reason_gender'])
        keyboard.row(LOCALE['btn_reason_birthday'])
        answer = bot.send_message(call.message.chat.id, LOCALE['msg_getReason'], reply_markup=keyboard)
        bot.register_next_step_handler(answer, get_reason)


bot.enable_save_next_step_handlers(delay=0.5)
bot.load_next_step_handlers()

bot.polling()

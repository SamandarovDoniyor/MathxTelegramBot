import random

import config

import templates

import telebot

from telebot import types

from app.models import BotUser, Game, Question


bot = telebot.TeleBot(
    token=config.TOKEN,
    parse_mode='Markdown',
    num_threads=5
)


def get_random_question():
    id_list = Question.objects.all().values_list('id', flat=True) 
    question_id = random.choice(id_list)
    return Question.objects.get(id=question_id)


def text_to_smiles(text):
    filtered_text = str()
    to_smile = {
        '0': '0️⃣',
        '1': '1️⃣',
        '2': '2️⃣',
        '3': '3️⃣',
        '4': '4️⃣',
        '5': '5️⃣',
        '6': '6️⃣',
        '7': '7️⃣',
        '8': '8️⃣',
        '9': '9️⃣',
        '+': '➕',
        '-': '➖',
        '/': '➗',
        '*': '✖️',
        '=': '='
    }

    for c in text:
        filtered_text += to_smile.get(c, c)

    return filtered_text


def make_question(question):
    if random.randint(1, 2) == 1:
        result = question.result
    else:
        result = question.result - 1
    
    return text_to_smiles(templates.QUESTION_INFO.format(
        first_value=question.first_value,
        second_value=question.second_value,
        operator=question.operator,
        result=result,
    )), result
   

@bot.message_handler(commands=['start'])
def start_command_handler(message):
    chat_id = message.chat.id
    if not BotUser.objects.filter(chat_id=chat_id).exists():
        full_name = message.chat.first_name
        if message.chat.last_name:
            full_name += ' ' + message.chat.last_name
        BotUser.objects.create(chat_id=chat_id, full_name=full_name)

    bot.send_message(
        chat_id=chat_id,
        text=templates.START_COMMAND_HANDLER,
    )


@bot.message_handler(commands=['new_game'])
def new_game_command_handler(message):
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    game = Game(user=user)
    game.save()
    question = get_random_question()
    text, result = make_question(question)
    keyboard = types.InlineKeyboardMarkup()
    data = f'{game.id} {question.id} {result}'
    true_button = types.InlineKeyboardButton(
        text='✔️',
        callback_data=data+' True',
    )
    false_button = types.InlineKeyboardButton(
        text='✖️',
        callback_data=data+' False',
    )
    keyboard.add(true_button, false_button)
    bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard
    )
    

@bot.callback_query_handler(func=lambda _: True)
def callback_query_handler(call):
    chat_id = call.message.chat.id
    game_id, question_id, result, button = call.data.split()
    game = Game.objects.get(id=game_id)
    question = Question.objects.get(id=question_id)
    result = int(result)
    if result == question.result and button == 'True' or \
            result != question.result and button == 'False':
        game.question_number += 1
        game.save()
        question = get_random_question()
        text, result = make_question(question)
        keyboard = types.InlineKeyboardMarkup()
        data = f'{game.id} {question.id} {result}'
        true_button = types.InlineKeyboardButton(
            text='✔️',
            callback_data=data+' True',
        )
        false_button = types.InlineKeyboardButton(
            text='✖️',
            callback_data=data+' False',
        )
        keyboard.add(true_button, false_button)
        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=call.message.id,
            reply_markup=keyboard,
        )
    else:
        game.user.record = max(game.user.record, game.question_number-1)
        game.user.save()
        text = templates.RESULT_INFO.format(
            balls=game.question_number-1,
            record=game.user.record,
        )
        bot.send_message(
            chat_id=chat_id,
            text=text,
        )
        bot.delete_message(
            chat_id=chat_id,
            message_id=call.message.id,
        )


bot.polling()
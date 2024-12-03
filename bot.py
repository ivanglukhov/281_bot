import telebot
from telebot import custom_filters, types
from telebot.types import ReplyParameters, InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs.log', level=logging.INFO)

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS survey (
      username VARCHAR,
      question1 VARCHAR,
      question2 VARCHAR,
      question3 INT,
      question4 INT,
      question5 VARCHAR,
      question6 INT,
      question7 VARCHAR,
      question8 INT,
      question9 VARCHAR,
      question10 VARCHAR,
      question11 VARCHAR,
      question12 VARCHAR,
      question13 VARCHAR,
      question14 VARCHAR,
      question15 VARCHAR
    )
''')

connection.commit()

def insert(test, data):
  cursor.execute('''
    INSERT INTO survey VALUES(?, ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
  ''', [test] + data)
  connection.commit()

survey = {
    1: {
        "text": "Какое у вас самое любимое блюдо/напиток? (можно несколько)",
        "type": "text"
    },
    2: {
        "text": "Какие блюда вам меньше всего нравятся, почему?",
        "type": "text"
    },
    3: {
        "text": "Как вы оцениваете качество еды в столовой? (1/10)",
        "type": "num",
        "range_start": 0,
        "range_end": 10
    },
    4: {
        "text": "Достаточно ли разнообразно меню столовой? (1/10)",
        "type": "num",
        "range_start": 0,
        "range_end": 10
    },
    5: {
        "text": "Как часто вы обедаете в школьной столовой? (совсем не обедаю/редко/часто)",
        "type": "choice",
        "options": ('совсем не обедаю', 'редко', 'часто')
    },
    6: {
        "text": "Как вы оцениваете работу персонала в школьной столовой? (1/10)",
        "type": "num",
        "range_start": 0,
        "range_end": 10
    },
    7: {
        "text": "Есть ли очереди в столовой, как долго приходится ждать? (недолго/долго)",
        "type": "choice",
        "options": ('недолго', 'долго')
    },
    8: {
        "text": "Достаточно ли у вас времени на обед? (1/10)",
        "type": "num",
        "range_start": 0,
        "range_end": 10
    },
    9: {
        "text": "Почему вы можете пропускать обед в школьной столовой?",
        "type": "text"
    },
    10: {
        "text": "Хватает ли посадочных мест в школьной столовой? (да/не совсем/нет)",
        "type": "choice",
        "options": ('нет', 'не совсем', 'да')
    },
    11: {
        "text": "Устраивают ли вас цены в школьной столовой? (да/нет)",
        "type": "choice",
        "options": ('да', 'нет')
    },
    12: {
        "text": "Чистые ли кухонные приборы в школьной столовой? (нет/не совсем/да)",
        "type": "choice",
        "options": ('нет', 'не совсем', 'да')
    },
    13: {
        "text": "Есть ли у вас аллергии или диетические предпочтения, которые не учитываются в меню? Если да, то какие?",
        "type": "text"
    },
    14: {
        "text": "Какие плюсы/минусы вы можете выделить в работе столовой?",
        "type": "text"
    },
    15: {
        "text": "Есть ли у вас предложения по улучшению школьного питания, какие?",
        "type": "text"
    }
}

survey_inline_markups = []
for i in range(1, len(survey.keys())+1):
  markup = telebot.types.InlineKeyboardMarkup()
  if survey[i]['type'] == 'choice':
    buttons = [
        InlineKeyboardButton(text=i, callback_data=i)
        for i in survey[i]['options']
    ]
    markup.add(*buttons)
    survey_inline_markups.append(markup)
  else:
    survey_inline_markups.append(0)





bot = telebot.TeleBot("8082285614:AAGh7cwWubcatBZSU3wULWuVUjuxVT1d1M8",
                      use_class_middlewares=True)


'''
  states = {
      'chat_id': ['answer1',...,'answern']
  }
'''
states = {

}



# Start command handler
@bot.message_handler(commands=["start"])
def start_ex(message: types.Message):
  global states
  chat_id = message.chat.id
  bot.send_message(
      message.chat.id,
      '''Спасибо, что решили принять участие в нашем опросе о качестве школьной столовой.
      Ваше мнение очень важно для нас! Опрос займет всего несколько минут.
      Пожалуйста, отвечайте честно и открыто — все ваши ответы останутся анонимными.''',
  )
  bot.send_message(
      message.chat.id,
      '''Какое у вас самое любимое блюдо/напиток? (можно несколько)''',
  )


  states[chat_id] = []

@bot.message_handler(content_types=["text"])
def text_answer(message):
  chat_id = message.chat.id
  answer = message.text
  states[chat_id].append(answer)
  current_state = len(states[chat_id])
  
  logger.info(str(chat_id) + str(states[chat_id]))
  if survey[current_state+1]['type'] == 'text' or survey[current_state+1]['type'] == 'num':
    bot.send_message(message.chat.id,survey[current_state+1]['text'])
  elif survey[current_state+1]['type'] == 'choice':
    bot.send_message(message.chat.id,survey[current_state+1]['text'],
                     reply_markup=survey_inline_markups[current_state])

  if current_state+1 == 15:
    bot.register_next_step_handler(message, finish)

@bot.callback_query_handler(func = lambda call: True)
def callback_query(call):
  chat_id = call.message.chat.id
  answer = call.data
  states[chat_id].append(answer)
  current_state = len(states[chat_id])

  logger.info(str(chat_id) + str(states[chat_id]))
  if survey[current_state+1]['type'] == 'text' or survey[current_state+1]['type'] == 'num':
    bot.send_message(call.message.chat.id,survey[current_state+1]['text'])
  elif survey[current_state+1]['type'] == 'choice':
    bot.send_message(call.message.chat.id,survey[current_state+1]['text'],
                     reply_markup=survey_inline_markups[current_state])

  if current_state+1 == 15:
    bot.register_next_step_handler(call.message, finish)

def finish(message):
  chat_id = message.chat.id
  answer = message.text
  states[chat_id].append(answer)
  current_state = len(states[chat_id])
  insert(chat_id, states[chat_id])
  states.pop(chat_id)
  bot.send_message(chat_id, 'Спасибо за участие в опросе! Для повторной введите команду start')
  

bot.polling(non_stop=True)

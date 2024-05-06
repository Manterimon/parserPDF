import py_pdf_parser
import pandas
from py_pdf_parser.visualise import visualise
from py_pdf_parser.loaders import load_file
import telebot
import webbrowser
from telebot import types
import requests
import os
import numpy


class ParserPDF:
    def __init__(self, doc):
        self.document = load_file(doc)
        print(self.document.page_numbers)

    def loadingtTextInThePDF(self, name: str, right_or_left: str) -> str:
        self.fioDoctor_element = self.document.elements.filter_by_text_equal(name).extract_single_element()

        if right_or_left == 'right':
            fioDoctor_text = self.document.elements.to_the_right_of(
                self.fioDoctor_element).extract_single_element().text()
            return fioDoctor_text
        elif right_or_left == 'left':
            fioDoctor_text = self.document.elements.to_the_left_of(
                self.fioDoctor_element).extract_single_element().text()
            return fioDoctor_text

    # def outputText(self):
    #     self.output = {
    #         'Врач': self.loadingtTextInThePDF(),
    #     }
    #     print(self.output)


API_TOKEN = '7133025823:AAGrZdsB1FKhh4JIV8IwAwtnKPV03MBqauk'
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def startNewChat(chat):
    bot.send_message(chat.chat.id, 'Привет, это бот <b>PDFFileParser</b> от <u>Manterimon</u>!'
                                   ' Этот бот был создан для того что бы удобно считывать'
                                   ' информацию из различных PDF файлов. Приятного использования!\n'
                                   ' Чтобы начать использовать бота, '
                                   'отправьте PDF файл в чат и дальше следуете инструкциям', parse_mode='html')


@bot.message_handler(commands=['del'])
def delete_PDF_file(chat):
    try:
        bot.send_message(chat.chat.id, 'PDF файл удален!')
        os.remove(f'temp_file{chat.chat.id}.pdf')
    except FileNotFoundError:
        bot.send_message(chat.chat.id, 'Произошла ошибка!\nВозможно такого файла нету,'
                                       ' попробуйте загрузить его еще раз')


@bot.message_handler(content_types=['document'])
def handle_docs(chat):
    try:
        file_info = bot.get_file(chat.document.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path))
        with open(f'temp_file{chat.chat.id}.pdf', 'wb') as new_file:
            new_file.write(file.content)
        # markup = types.InlineKeyboardMarkup()

        bot.send_message(chat.chat.id, '<b>Файл был успешно загружен!</b>\n'
                                       'Пожалуйста, укажите ключевое слово для ориентации. '
                                       '<em>В случае необходимости</em>, ключевое слово следует вводить вместе с двоеточиями, '
                                       'согласно примеру представленному ниже.'
                                       '\n <u>Информация</u> <b> - Указанное ключевое слово:</b> <u>Информация</u>',
                         parse_mode='html')
        request_keyword(chat)
    except Exception as e:
        bot.reply_to(chat, 'Произошла ошибка при обработке файла')
        bot.send_message(chat.chat.id, f'{e}')


def input_key_word(chat):
    if chat.text:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Инф. расп. слево', callback_data='returnLeftInfo')
        btn2 = types.InlineKeyboardButton('Инф. расп. справо', callback_data='returnRithInfo')
        markup.add(types.InlineKeyboardButton('Изменить ключевое слово', callback_data='input_key_word'))
        markup.row(btn1, btn2)
        bot.send_message(chat.chat.id, f'Ключевое слово: {chat.text}', reply_markup=markup)

    else:
        bot.send_message(chat.chat.id, 'Произошла ошибка, попробуйте еще раз!')
        bot.register_next_step_handler(chat, input_key_word)


def request_keyword(chat):
    bot.send_message(chat.chat.id, 'Пожалуйста, введите ключевое слово')
    bot.register_next_step_handler(chat, input_key_word)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'input_key_word':
        request_keyword(call.message)

@bot.callback_query_handler(func=lambda call: call.data in ['returnLeftInfo', 'returnRithInfo'])
def parsAndReturnText(call):
    chat_id = call.message.chat.id
    if call.data in ['returnLeftInfo', 'returnRithInfo']:
        try:
            with open(f'temp_file{chat_id}.pdf', 'rb') as new_file:
                pars = ParserPDF(new_file)
                keyword = call.message.chat.text
                print(keyword)
                retText = pars.loadingtTextInThePDF(keyword, 'left' if call.data == 'returnLeftInfo' else 'right')
                bot.send_message(chat_id, retText)
        except Exception as e:
            bot.send_message(chat_id, f'Произошла ошибка: {e}')


bot.polling(none_stop=True)

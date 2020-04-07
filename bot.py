# -*- coding: utf-8 -*-
import telebot
from telebot import types
import config
import dbworker

bot = telebot.TeleBot(config.TOKEN)

# Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    # если /start написал авторизовавшийся пользователь
    if dbworker.get_current_state(message.chat.id) == config.States.AUTHORIZATED.value:
        # подключаемся к БД
        conn = dbworker.SQLighter()
        # Спрашиваем: это админ?
        answer = conn.is_admin(message.from_user.id)
        # закрываем подключение к базе
        conn.close()

        # если это одмен
        if answer:
            bot.send_message(message.from_user.id, "Начнём работу, Администратор")
        else:
            # не одмен
            bot.send_message(message.from_user.id, "Начнём работу, Менаджер")
    else:
        # /start написал НЕ авторизовавшийся пользователь
        bot.send_message(message.chat.id, "Напиши кто ты по масти")
        dbworker.set_state(message.chat.id, config.States.START_ENTER.value)

# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Начнём с начала")
    dbworker.set_state(message.chat.id, config.States.START_ENTER.value)

# Обрабатывается в первом состоянии - когда нужно ввести admin или manager
# Состояние - старт
# обрабатывает любы сообщения можно настроить 
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.START_ENTER.value)
def user_entering_name(message):
    if message.text == 'admin':
        bot.send_message(message.chat.id, "Приветствую повелитель, но введи сначала пароль")
        dbworker.set_state(message.chat.id, config.States.ENTER_PASSWOD.value)
    elif message.text == 'manager':
        bot.send_message(message.chat.id, "Дарова роботяга! Введи имя организации")
        dbworker.set_state(message.chat.id, config.States.ENTER_COMPANY.value)
    else:
        bot.send_message(message.chat.id, "Введи 'admin' или 'manager'")

# Обрабатывается когда нужно ввести пароль
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.ENTER_PASSWOD.value)
def user_entering_password(message):
    if message.text == '12345678':
        # поключаемся к базе данных
        conn = dbworker.SQLighter()
        # Получаем ответ от БД
        answer = conn.add_admin(message.from_user)
        # закрываем соединение
        conn.close()

        if not answer:
            # пользователь уже есть в таблице админов
            bot.send_message(message.chat.id, "Добро пожаловать снова")
        else:
            # Новый админ
            bot.send_message(message.chat.id, "Я записал тебя в список админов")
        dbworker.set_state(message.chat.id, config.States.AUTHORIZATED.value)
    else:
        bot.send_message(message.chat.id, "Неправильный пароль, попробуй снова")

# Обрабатывается когда нужно ввести имя компании
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.ENTER_COMPANY.value)
def user_work(message):
        # подключаемся к базе
        conn = dbworker.SQLighter()
        if not conn.add_manager(message.from_user, message.text):
            # пользователь уже есть в таблице админов
            # обновим его поля
            conn.update_manager(message.from_user, company=message.text)
            # Закрываем соединение
            conn.close()
            bot.send_message(message.chat.id, "Имя компании успешно изменено")
        else:
            # Новый менаджер
            bot.send_message(message.chat.id, "Добро пожаловать на каторгу")

        dbworker.set_state(message.chat.id, config.States.AUTHORIZATED.value)

# Обрабатывается когда пользователь уже зарегестрирован
# Пишем разные сообщения в зависимосты кто это
# Тут обрабатываются пока текстовые сообщения, но это можно настроить
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.AUTHORIZATED.value)
def user_working(message):
    # подключаемся к базе
        conn = dbworker.SQLighter()
        # Спрашиваем: "Это Одмен?"
        answer = conn.is_admin(message.from_user.id)
        # Закрываем соединение с базой
        conn.close()

        # Если Админ можно зафигачить кастомную клавиатуру или тп
        if answer:
            bot.send_message(message.from_user.id, 'Адмен привет. Такое дело не пиши мне')
        else:
            # Не одмен
            bot.send_message(message.from_user.id, 'Манагер дарова. Иди работать, не пиши мне')


if __name__ == "__main__":
    # bot.send_message(config.ADMIN_ID, 'Бот запущен')
    bot.infinity_polling()
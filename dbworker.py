# -*- coding: utf-8 -*-
import config
import sqlite3
from vedis import Vedis

class SQLighter:
    """Работает с базой sqlite"""
    def __init__(self, database=config.db_users):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_list_admin_ids(self):
        """Получаем список id всех админов"""
        rows = self.cursor.execute("SELECT id FROM admins").fetchall()
        return [row[0] for row in rows]

    def is_admin(self, user_id):
        """Проверяем является ли пользователь админом"""
        return user_id in self.get_list_admin_ids()

    def add_admin(self, user):
        """Добавляем админа в таблицу админов"""
        if not self.is_admin(user.id):
            with self.connection:
                self.cursor.execute("INSERT INTO admins VALUES (?,?,?,?)", 
                                    (user.id,
                                     user.username,
                                     user.first_name,
                                     user.last_name))
            return True
        return False
    
    def get_all_admins(self):
        """Получаем ВСЕХ админов"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM admins").fetchall()

    def get_admin(self, user_id):
        """Получаем параметры ОДНОГО админа из БД"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM admins WHERE id=?", (user_id,)).fetchone()

    def count_admins(self):
        """Количество Админов"""
        return len(self.get_all_admins())


    def get_list_manager_ids(self):
        """Получаем список id всех менаджеров"""
        rows =  self.cursor.execute("SELECT id FROM managers").fetchall()
        return [row[0] for row in rows]
    
    def is_manager(self, user_id):
        """Проверяем является ли пользователь менаджером"""
        return user_id in self.get_list_manager_ids()
    
    def add_manager(self, user, company):
        """Добавляем менаджера в таблицу"""
        if not self.is_manager(user.id):
            with self.connection:
                self.cursor.execute("INSERT INTO managers VALUES (?,?,?,?,?)", 
                                    (user.id,
                                     company,
                                     user.username,
                                     user.first_name,
                                     user.last_name))
            return True
        return False
    
    def get_all_managers(self):
        """Получаем ВСЕХ менаджеров"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM managers").fetchall()

    def get_manager(self, user_id):
        """Получаем параметры ОДНОГО менаджера из БД"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM managers WHERE id=?", (user_id,)).fetchone()
    
    def update_manager(self, user, company):
        """Изменяем поля менаджера - пока что это только компания"""
        with self.connection:
            self.cursor.execute("UPDATE managers SET company=? WHERE id=?", (company, user.id))


    def count_managers(self):
        """Количество Менаджеров"""
        return len(self.get_all_managers())

    def close(self):
        """Закрываем текущее соединение с БД"""
        self.connection.close()


# Работаем теперь с СОСТОЯНИЯМИ пользоватлей
def get_current_state(user_id):
    """
    Пытаемся узнать из базы состояний "состояние" пользователя
    """
    with Vedis(config.db_states) as db:
        try:
            state = db[user_id].decode()
        except KeyError: # если такого ключа не оказалось
            # берём значение по умолчанию
            state = config.States.START_ENTER.value
        return state


def set_state(user_id, value):
    """
    Сохраняем текущее «состояние» пользователя в нашу базу состояний
    """
    with Vedis(config.db_states) as db:
        try:
            db[user_id] = value
            return True
        except:
            # тут желательно как-то обработать ситуацию
            # но врядли что-то такое случится
            return False
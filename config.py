# -*- coding: utf-8 -*-
from enum import Enum

TOKEN = ''
# ADMIN_ID = 182826395
db_users = 'bases/users.db'  # Файл с базой данных о пользователях
db_states = 'bases/states.vdb'  # Файл с базой данных о состояних

class States(Enum):
    START_ENTER = '0'
    ENTER_PASSWOD = '1'
    ENTER_COMPANY = '2'
    AUTHORIZATED = '3'
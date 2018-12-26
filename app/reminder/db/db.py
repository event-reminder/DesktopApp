import os
import peewee

from app.settings.custom_settings import DB_PATH, DB_FILE


if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

database_instance = peewee.SqliteDatabase(DB_PATH + DB_FILE)

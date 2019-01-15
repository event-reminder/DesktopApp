import os
import peewee

from app.settings.default.app import APP_DB_PATH, APP_DB_FILE


if not os.path.exists(APP_DB_PATH):
    os.makedirs(APP_DB_PATH)

database_instance = peewee.SqliteDatabase(APP_DB_FILE)

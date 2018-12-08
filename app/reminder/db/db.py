import peewee

from app.settings.custom_settings import DB_PATH


database_instance = peewee.SqliteDatabase(DB_PATH)

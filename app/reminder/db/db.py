import peewee

from app.reminder.db.settings import DB_PATH


database_instance = peewee.SqliteDatabase(DB_PATH)

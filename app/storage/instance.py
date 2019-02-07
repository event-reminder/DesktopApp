import os
import peewee

from app.settings.default import APP_DB_PATH, APP_DB_FILE


if not os.path.exists(APP_DB_PATH):
	os.makedirs(APP_DB_PATH)

DATABASE_INSTANCE = peewee.SqliteDatabase(APP_DB_FILE)

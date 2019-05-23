# noinspection SqlDialectInspection,SqlNoDataSourceInspection
QUERY_CREATE_EVENT_TABLE = """
CREATE TABLE IF NOT EXISTS Events (
  id                INTEGER      NOT NULL PRIMARY KEY,
  title             VARCHAR(500) NOT NULL,
  date              DATE         NOT NULL,
  time              TIME         NOT NULL,
  description       TEXT         NOT NULL,
  is_past           INTEGER      NOT NULL,
  repeat_weekly     INTEGER      NOT NULL,
  is_notified       INTEGER      DEFAULT 0
);
"""

# noinspection SqlDialectInspection,SqlNoDataSourceInspection
QUERY_SELECT_EVENT_BY_ID = """
SELECT * FROM Events WHERE id = {};
"""

# noinspection SqlDialectInspection,SqlNoDataSourceInspection
QUERY_DELETE_ALL_EVENTS = """
DELETE FROM Events;
"""

# noinspection SqlDialectInspection,SqlNoDataSourceInspection
QUERY_INSERT_EVENT = """
INSERT INTO Events(title, date, time, description, is_past, repeat_weekly)
  VALUES (?, ?, ?, ?, ?, ?);
"""

# noinspection SqlDialectInspection,SqlNoDataSourceInspection
QUERY_UPDATE_EVENT = """
UPDATE Events SET title = ?, date = ?, time = ?, description = ?, is_past = ?, repeat_weekly = ?, is_notified = ?
  WHERE id = ?;
"""

# noinspection SqlDialectInspection,SqlNoDataSourceInspection
QUERY_DELETE_EVENT_BY_ID = """
DELETE FROM Events WHERE id = ?;
"""

# noinspection SqlDialectInspection,SqlNoDataSourceInspection
QUERY_SELECT_EVENTS_BY = """
SELECT * FROM Events {};
"""

QUERY_CREATE_EVENT_TABLE = """
CREATE TABLE IF NOT EXISTS Events(
  id            INTEGER      NOT NULL PRIMARY KEY,
  title         VARCHAR(500) NOT NULL,
  datetime      DATETIME     NOT NULL,
  description   TEXT         NOT NULL,
  is_past       INTEGER      NOT NULL,
  repeat_weekly INTEGER      NOT NULL
);
"""

QUERY_SELECT_EVENT_BY_ID = """
SELECT * FROM Events WHERE id = {};
"""

QUERY_DELETE_ALL_EVENTS = """
DELETE FROM Events WHERE TRUE;
"""

QUERY_INSERT_EVENT = """
INSERT INTO Events(title, datetime, description, is_past, repeat_weekly) VALUES (?, ?, ?, ?, ?);
"""

QUERY_UPDATE_EVENT = """
UPDATE Events SET title = ?, datetime = ?, description = ?, is_past = ?, repeat_weekly = ? WHERE id = ?;
"""

QUERY_DELETE_EVENT_BY_ID = """
DELETE FROM Events WHERE id = ?;
"""

QUERY_SELECT_EVENTS_BY = """
SELECT * FROM Events {};
"""

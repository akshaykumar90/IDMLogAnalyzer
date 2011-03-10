import os
import sqlite3

db_filename = 'logan.db'
schema_filename = 'logan_schema.sql'

db_is_new = not os.path.exists(db_filename)

conn = sqlite3.connect(db_filename)

if db_is_new:
    print 'Creating schema'
    f = open(schema_filename, 'rt')
    schema = f.read()
    f.close()
    conn.executescript(schema)
else:
    print 'Database exists, assume schema does, too.'

conn.close()
import psycopg2
import psycopg2.extras
"""def connect():
    conn = psycopg2.connect(
        host="localhost",             # PostgreSQL server (localhost for local machine)
        dbname="shop",         # Your database name
        user="walid",
        password="abcd",# Use the 'postgres' superuser
        cursor_factory = psycopg2.extras.NamedTupleCursor,
    )
    conn.autocommit = True
    return conn
"""

def connect():
    conn = psycopg2.connect(
        host="sqledu.univ-eiffel.fr",             # PostgreSQL server (localhost for local machine)
        dbname="walid.ramtani_db",         # Your database name
        password="JunMis#16544",# Use the 'postgres' superuser
        cursor_factory = psycopg2.extras.NamedTupleCursor,
    )
    conn.autocommit = True
    return conn

# Database-related code.

# sudo apt-get install sqlite3
import sqlite3

conn = None

# Query helpers.

def query(conn, cmd, *parameters):
    return list(conn.execute(cmd, *parameters))

def query_single_row(conn, cmd, *parameters):
    rows = query(conn, cmd, *parameters)
    return rows[0] if rows else None

def query_single_value(conn, cmd, *parameters):
    row = query_single_row(conn, cmd, *parameters)
    return row[0] if row is not None else None

def db_upgrade0(conn):
    conn.execute('''CREATE TABLE temp (
        id INTEGER PRIMARY KEY,
        actual_temp REAL,
        set_temp REAL,
        heater_on INTEGER,
        recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

UPGRADES = [
    db_upgrade0,
]

def upgrade_schema(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)")

    current_version = query_single_value(conn, "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
    start_version = current_version + 1 if current_version is not None else 0

    for upgrade_version in range(start_version, len(UPGRADES)):
        print("Applying upgrade %d" % upgrade_version)
        upgrade = UPGRADES[upgrade_version]
        upgrade(conn)
        conn.execute("INSERT INTO schema_version VALUES (?)", (upgrade_version,))

    conn.commit()

    print("There are %d entries in historical table" %
        query_single_value(conn, "SELECT count(*) FROM temp"))


def init():
    global conn
    conn = sqlite3.connect("data.db")
    upgrade_schema(conn)

def record(actual_temp, set_temp, heater_on):
    global conn
    conn.execute('''INSERT INTO temp (actual_temp, set_temp, heater_on) VALUES (?, ?, ?)''',
            (actual_temp, set_temp, heater_on))
    conn.commit()
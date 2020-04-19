import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def open_db_connection():
    conn = sqlite3.connect('db/todo.db')
    conn.row_factory = dict_factory
    cursor = conn.cursor()

    return cursor, conn


def create_db_table(cur, conn):
    query = """
        CREATE TABLE IF NOT EXISTS todo (id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        todo_timestamp TIMESTAMP DEFAULT NULL,
        todo_date DATE,
        note TEXT,
        scheduled_date DATE,
        priority INT,
        is_done INT DEFAULT 0
        )
    """
    cur.execute(query)
    conn.commit()


def insert_into_table(cur, task, conn):
    sql = '''
        INSERT INTO todo(task, todo_timestamp, todo_date, scheduled_date) VALUES(?, datetime('now','localtime'), date(), date())
    '''
    cur.execute(sql, (task,))
    conn.commit()

def update_row(**kwargs):
    cur = kwargs.pop("cursor")
    conn = kwargs.pop("connection")
    data = kwargs.pop("data")
    rowid = kwargs.pop("rowid")

    query = "UPDATE todo SET {} WHERE id={}"
    data_n = ""
    for key, val in data.items():
        if val and isinstance(val, str):
            data_n += "{}='{}', ".format(key, val)
        elif val and isinstance(val, int):
            data_n += "{}={}, ".format(key, val)
    data_n = data_n.rstrip(", ")

    query = query.format(data_n, rowid)
    try:
        cur.execute(query)
        conn.commit()
    except:
        print("Error in build query: %s. Missing data or rowid" % query)


def connect_sqlite_db():
    conn = sqlite3.connect('db/todo.db')
    cursor = conn.cursor()

    return cursor

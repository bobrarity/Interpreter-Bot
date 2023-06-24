import sqlite3


database = sqlite3.connect('bot.db')

cursor = database.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS history(
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id BIGINT,
        src TEXT,
        dest TEXT,
        original_text TEXT,
        translated_text TEXT
    );

''')
database.commit()
database.close()


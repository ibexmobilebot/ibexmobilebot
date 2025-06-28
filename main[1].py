from flask import Flask, request
import sqlite3
import random

app = Flask(__name__)
BOT_TOKEN = "934305552:kMVFrAWkzSGUrYgSkQMuMgBBbipE2cCKfnETDwE9"
CHANNEL_ID = "@ibexmobile"

def init_db():
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        inviter_id TEXT,
        joined INTEGER DEFAULT 1
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        code TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS winners (
        user_id TEXT,
        name TEXT,
        phone TEXT,
        prize TEXT
    )''')
    conn.commit()
    conn.close()

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    if not data.get('message'):
        return 'ok'

    user_id = str(data['message']['from']['user']['id'])
    text = data['message'].get('text', '')
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()

    if text.startswith("/start"):
        parts = text.split(" ")
        if len(parts) > 1:
            inviter = parts[1]
            if inviter != user_id:
                c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
                if not c.fetchone():
                    c.execute("INSERT INTO users (user_id, inviter_id) VALUES (?, ?)", (user_id, inviter))
                    code = str(random.randint(1000000, 9999999))
                    c.execute("INSERT INTO chances (user_id, code) VALUES (?, ?)", (inviter, code))
                    conn.commit()
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    elif text == "/draw":
        c.execute("SELECT user_id, code FROM chances ORDER BY RANDOM() LIMIT 30")
        winners = c.fetchall()
        prizes = ['ساعت هوشمند'] * 2 + ['ایرپاد'] * 3 + ['کد تخفیف ۲۰۰ هزار تومانی'] * 25
        for i, (uid, code) in enumerate(winners):
            prize = prizes[i]
            c.execute("INSERT INTO winners (user_id, prize) VALUES (?, ?)", (uid, prize))
        conn.commit()
    conn.close()
    return "ok"

if __name__ == "__main__":
    init_db()
    app.run()

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import mysql.connector
import json
import re


app = Flask(__name__)
Bootstrap(app)

def connect_to_db():

    db_config = {
        "host": "127.0.0.1",
        "user": "root",
        "password": "",
        "database": "discord_messages"
    }
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    return cursor, conn


def select_all_from_db_np(sql_query):
    try:
        cursor, conn = connect_to_db()

        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.close()

        return result

    except Exception as e:
        print("SQL_Secure.select_all_from_db_np: ", e)
        return False


def extract_items(s: str) -> list:
    """Extract item names enclosed in square brackets from a given string."""
    return re.findall(r'\[([^\]]+)\]', s)


@app.route('/')
def index():
    data = select_all_from_db_np("SELECT title, username, field, mob, loot, timestamp FROM messages ORDER BY timestamp DESC LIMIT 20")
    data_list = []
    for i in data:
        data_list.append(json.loads(i['loot']))
    print(data_list)

    leaderboard = select_all_from_db_np("SELECT username, SUM(field) as total_field FROM messages GROUP BY username ORDER BY total_field DESC LIMIT 20")
    print(leaderboard)

    return render_template('index.html', loot=data_list, data=data, leaderboard=leaderboard )


if __name__ == '__main__':
    app.run(debug=True)

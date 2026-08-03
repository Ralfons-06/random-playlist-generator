from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__, template_folder='../templates')
DB_PATH = "/app/data/history.db"

@app.route("/")
def index():
    if not os.path.exists(DB_PATH):
        return "Noch keine Daten vorhanden. Skript muss zuerst ausgeführt werden."

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("SELECT pool_size FROM executions ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        pool_size = row["pool_size"] if row else 0
        
        cur.execute("SELECT name, artist, selection_count FROM tracks ORDER BY selection_count DESC LIMIT 50")
        top_tracks = cur.fetchall()
        
        cur.execute("SELECT id, timestamp, pool_size FROM executions ORDER BY timestamp DESC LIMIT 15")
        executions = cur.fetchall()
        
    return render_template("index.html", pool_size=pool_size, top_tracks=top_tracks, executions=executions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
from flask import Flask, render_template
import sqlite3
import os
import json

app = Flask(__name__, template_folder='../templates')
DB_PATH = "data/history.db"

@app.route("/")
def index():
    if not os.path.exists(DB_PATH):
        return "Noch keine Daten vorhanden. Skript muss zuerst ausgeführt werden."

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) as pool_size FROM tracks")
        pool_size = cur.fetchone()["pool_size"]
        
        cur.execute("SELECT name, artist, image_url, execution_ids FROM tracks")
        all_tracks = cur.fetchall()
        
        cur.execute("SELECT id, timestamp, status FROM executions ORDER BY timestamp DESC LIMIT 15")
        executions = cur.fetchall()

    tracks_processed = []
    for t in all_tracks:
        exec_ids = json.loads(t["execution_ids"])
        tracks_processed.append({
            "name": t["name"],
            "artist": t["artist"],
            "image_url": t["image_url"],
            "selection_count": len(exec_ids)
        })
        
    top_tracks = sorted(tracks_processed, key=lambda x: x["selection_count"], reverse=True)[:50]
        
    return render_template("index.html", pool_size=pool_size, top_tracks=top_tracks, executions=executions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
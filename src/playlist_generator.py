import os
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
import my_config
from typing import List
import sqlite3
import datetime
import json

PLAYLIST_NAME = "WEEKLY ROTATION"
TRACK_NO = 60
SCOPES = "user-library-read playlist-modify-private playlist-modify-public"
DB_PATH = "data/history.db"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaylistGenerator:
    def __init__(self):
        self.client = self._get_spotify_client()
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS executions (id INTEGER PRIMARY KEY, timestamp TEXT, status TEXT)")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    uri TEXT PRIMARY KEY, 
                    name TEXT, 
                    artist TEXT, 
                    album TEXT, 
                    release_year TEXT,
                    duration_ms INTEGER,
                    popularity INTEGER,
                    is_explicit INTEGER,
                    image_url TEXT,
                    spotify_url TEXT,
                    execution_ids TEXT
                )
            """)

    def _save_tracks(self, exec_id: int, tracks: List[dict]):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            for t in tracks:
                uri = t["uri"]
                name = t["name"]
                artist = t["artists"][0]["name"] if t.get("artists") else "Unknown"
                album = t.get("album", {}).get("name", "Unknown")
                
                release_date = t.get("album", {}).get("release_date", "")
                release_year = release_date[:4] if release_date else "Unknown"
                
                duration_ms = t.get("duration_ms", 0)
                popularity = t.get("popularity", 0)
                is_explicit = 1 if t.get("explicit") else 0
                
                images = t.get("album", {}).get("images", [])
                image_url = images[0].get("url", "") if images else ""
                spotify_url = t.get("external_urls", {}).get("spotify", "")
                
                cur.execute("SELECT execution_ids FROM tracks WHERE uri = ?", (uri,))
                row = cur.fetchone()
                
                if row:
                    exec_ids = json.loads(row[0])
                    if exec_id not in exec_ids:
                        exec_ids.append(exec_id)
                    cur.execute("""
                        UPDATE tracks 
                        SET execution_ids = ?, popularity = ?
                        WHERE uri = ?
                    """, (json.dumps(exec_ids), popularity, uri))
                else:
                    exec_ids = [exec_id]
                    cur.execute("""
                        INSERT INTO tracks (uri, name, artist, album, release_year, duration_ms, popularity, is_explicit, image_url, spotify_url, execution_ids) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (uri, name, artist, album, release_year, duration_ms, popularity, is_explicit, image_url, spotify_url, json.dumps(exec_ids)))

    def run(self):
        logger.info("START: PLAYLIST GENERATION")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO executions (timestamp, status) VALUES (?, ?)", (timestamp, "running"))
            exec_id = cur.lastrowid
            
        status = "failed"
        try:
            pool_size = self.client.current_user_saved_tracks(limit=1)["total"]
            tracks = self.get_tracks(TRACK_NO, pool_size)
            track_uris = [track["uri"] for track in tracks]

            success = self.create_random_playlist(PLAYLIST_NAME, track_uris)
            if success:
                self._save_tracks(exec_id, tracks)
                status = "worked"
                logger.info("Spotify Playlist successfully refreshed")
        except Exception as e:
            logger.error(f"Error during generation: {e}")
        finally:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("UPDATE executions SET status = ? WHERE id = ?", (status, exec_id))

    def get_tracks(self, number_of_tracks: int, total: int) -> List[dict]:
        """Get tracks from your library (or other search)"""
        random_tracks = []
        track_uris = set()
        
        while len(random_tracks) < number_of_tracks:
            offset = random.randrange(total)
            response = self.client.current_user_saved_tracks(1, offset)
            if not response['items']:
                continue
                
            track = response['items'][0]['track']
            if track['uri'] not in track_uris:
                random_tracks.append(track)
                track_uris.add(track['uri'])
                
        return [track for track in random_tracks]

    def create_random_playlist(self, name: str, track_uris: List[str]) -> bool:
        """Create or replace a playlist with tracks"""
        user_id = self.client.me()["id"]
        # check if playlist exists
        playlists = self.client.user_playlists(user_id)
        playlist_id = None
        for p in playlists["items"]:
            if p["name"] == name:
                playlist_id = p["id"]
                break

        if not playlist_id:
            playlist = self.client.user_playlist_create(user=user_id, name=name, public=False)
            playlist_id = playlist["id"]

        # Replace playlist items
        self.client.playlist_replace_items(playlist_id, track_uris)
        return True

    def _get_spotify_client(self) -> spotipy.Spotify:
        """Create Spotify client using refresh token flow"""
        sp_oauth = SpotifyOAuth(
            client_id=my_config.client_id,
            client_secret=my_config.client_secret,
            redirect_uri=my_config.redirect_uri,
            scope=SCOPES,
            cache_path="/app/data/.spotify_token_cache"  # stores refresh token locally
        )
        token_info = sp_oauth.get_cached_token()
        if not token_info:
            # First-time: open browser to log in + approve scopes
            auth_url = sp_oauth.get_authorize_url()
            print("Open this URL in your browser to authorize the app:")
            print(auth_url)
            code = input("Enter the URL you were redirected to: ")
            code = sp_oauth.parse_response_code(code)
            token_info = sp_oauth.get_access_token(code)
            logger.info("Access token obtained and cached.")

        return spotipy.Spotify(auth=token_info["access_token"])


if __name__ == "__main__":
    gen = PlaylistGenerator()
    gen.run()
import random

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
import my_config
from typing import List

PLAYLIST_NAME = "WEEKLY ROTATION"
TRACK_NO = 60
SCOPES = "user-library-read playlist-modify-private playlist-modify-public"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaylistGenerator:
    def __init__(self):
        self.client = self._get_spotify_client()

    def _get_spotify_client(self) -> spotipy.Spotify:
        """Create Spotify client using refresh token flow"""
        sp_oauth = SpotifyOAuth(
            client_id=my_config.client_id,
            client_secret=my_config.client_secret,
            redirect_uri=my_config.redirect_uri,
            scope=SCOPES,
            cache_path=".spotify_token_cache"  # stores refresh token locally
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

    def run(self):
        logger.info("START: PLAYLIST GENERATION")
        tracks = self.get_tracks(TRACK_NO)
        track_uris = [track["uri"] for track in tracks]
        success = self.create_random_playlist(PLAYLIST_NAME, track_uris)
        if success:
            logger.info("Spotify Playlist successfully refreshed")

    def get_tracks(self, number_of_tracks: int) -> List[dict]:
        """Get tracks from your library (or other search)"""
        total = self.client.current_user_saved_tracks(limit=1)["total"]
        random_tracks = []
        for _ in range(number_of_tracks + 1):
            offset = random.randrange(total - 1)
            response = self.client.current_user_saved_tracks(1, offset)
            track = [temp_track for temp_track in response['items']]
            if track not in random_tracks:
                random_tracks.append(track)
        return [temp_track[0]['track'] for temp_track in random_tracks[:]]

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


if __name__ == "__main__":
    gen = PlaylistGenerator()
    gen.run()

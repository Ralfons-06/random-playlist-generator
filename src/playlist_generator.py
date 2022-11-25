from spotify_client import SpotifyClient
import time
import logging
import aiohttp
import asyncio
import json
import os
import config


PLAYLIST_NAME = "WEEKLY ROTATION"

LOG_LEVEL = "Info"

TRACK_NO = "track_no"


class PlaylistGenerator:

    def __init__(self):
        self.dc = config.sp_dc
        self.key = config.sp_key
        self.log = Log

    def run(self, *args):
        self.log("START: PLAYLIST GENERATION")
        track_no = 60

        client = SpotifyClient(token=self.get_spotify_token())
        tracks = client.get_tracks(track_no)
        track_uris = [track['uri'] for track in tracks]
        success = client.create_random_playlist(PLAYLIST_NAME, track_uris)
        if success:
            self.log("Spotify Playlist successfully refreshed")

    def get_token_instance(self):
        self.log("Setting up Token")
        return SpotifyToken(self.dc, self.key)

    def get_spotify_token(self):
        return self.get_token_instance().access_token


# source: https://github.com/fondberg/spotcast/blob/master/custom_components/spotcast/spotcast_controller.py
class SpotifyToken:
    """Represents a spotify token for an account."""

    sp_dc = None
    sp_key = None
    _access_token = None
    _token_expires = 0

    def __init__(self, sp_dc, sp_key):
        self.sp_dc = sp_dc
        self.sp_key = sp_key

    def ensure_token_valid(self):
        if float(self._token_expires) > time.time():
            return True
        self.get_spotify_token()

    @property
    def access_token(self):
        self.ensure_token_valid()
        return self._access_token

    def get_spotify_token(self):
        try:
            helper = TokenHelper(self.sp_dc, self.sp_key)
            self._access_token, self._token_expires = asyncio.run(helper.start_session())
            expires = self._token_expires - int(time.time())
            return self._access_token, expires
        except:  # noqa: E722
            print("bloed gelaufen")

class TokenHelper:
    sp_dc = None
    sp_key = None
    def __init__(self, sp_dc: str, sp_key: str) -> None:
        self.sp_dc = sp_dc
        self.sp_key = sp_key

    async def start_session(self):
        """ Starts session to get access token. """
        cookies = { 'sp_dc': self.sp_dc, 'sp_key': self.sp_key }
        async with aiohttp.ClientSession(cookies=cookies) as session:
            headers = { 'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36" }
            async with session.get('https://open.spotify.com/get_access_token?reason=transport&productType=web_player', allow_redirects=False, headers=headers) as response:
                if(response.status != 200):
                    return None, None
                data = await response.text()
                config = json.loads(data)
                access_token = config['accessToken']
                expires_timestamp = config['accessTokenExpirationTimestampMs']
                expiration_date = int(expires_timestamp) // 1000
                return access_token, expiration_date


class Log:

    def __new__(cls, *args, **kwargs):
            return super().__new__(cls)
            
    
    def __init__(self, msg):
        logging.basicConfig(filename='.log', encoding='utf-8', level=logging.INFO)
        logging.info(msg)


if __name__ == '__main__':
    gen = PlaylistGenerator()
    gen.run()
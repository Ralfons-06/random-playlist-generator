from spotify_client import SpotifyClient
import appdaemon.plugins.hass.hassapi as hass
import datetime
import time

import spotify_token as st


PLAYLIST_NAME = "WEEKLY ROTATION"

LOG_LEVEL = "Info"

CONF_SP_DC = "sp_dc"
CONF_SP_KEY = "sp_key"


class playlist_generator(hass.Hass):

    def initialize(self):
        self.dc = self.args[CONF_SP_DC]
        self.key = self.args[CONF_SP_KEY]

        runtime = self.parse_time("00:00:00")
        self.run_daily(self.run, runtime, constrain_days="sun")

    def run(self, kwargs):
        self.log("START: PLAYLIST GENERATION")
        client = SpotifyClient(token=self.get_spotify_token())
        tracks = client.get_tracks()
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
            self._access_token, self._token_expires = st.start_session(
                self.sp_dc, self.sp_key
            )
            expires = self._token_expires - int(time.time())
            return self._access_token, expires
        except:  # noqa: E722
            print("blöd gelaufen")

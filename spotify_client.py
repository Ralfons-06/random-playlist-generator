import random
import spotipy
from spotipy import SpotifyOAuth


class SpotifyClient:

    def __init__(self, scope):
        self.client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    def get_tracks(self):

        total = self.client.current_user_saved_tracks(limit=1)["total"]
        random_tracks = []
        i = 0
        while i in range(50):
            offset = random.randrange(total - 1)
            response = self.client.current_user_saved_tracks(1, offset)
            track = [temp_track for temp_track in response['items']]
            if track not in random_tracks:
                random_tracks.append(track)
                i += 1
        tracks = [temp_track[0]['track'] for temp_track in random_tracks[:]]

        return tracks

    def create_random_playlist(self, name, tracks):
        response = self.client.current_user_playlists()
        playlists = [playlist for playlist in response['items']]

        plid = None
        for i in range(len(playlists)):
            if playlists[i]['name'] == name:
                plid = playlists[i]['id']
                break
        if plid is not None:
            replace = self.client.playlist_replace_items(plid, tracks)
        else:
            user = self.client.current_user()["id"]
            plid = self.client.user_playlist_create(user, name)["id"]
            self.client.playlist_replace_items(plid, tracks)
        return True

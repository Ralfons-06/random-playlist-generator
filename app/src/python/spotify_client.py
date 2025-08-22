import random
import spotipy


class SpotifyClient:

    def __init__(self, token):
        self.client = spotipy.Spotify(auth=token)

    def get_tracks(self, number_of_tracks):
        total = self.client.current_user_saved_tracks(limit=1)["total"]
        random_tracks = []
        for _ in range(number_of_tracks + 1):
            offset = random.randrange(total - 1)
            response = self.client.current_user_saved_tracks(1, offset)
            track = [temp_track for temp_track in response['items']]
            if track not in random_tracks:
                random_tracks.append(track)
        return [temp_track[0]['track'] for temp_track in random_tracks[:]]

    def create_random_playlist(self, name, tracks):
        response = self.client.current_user_playlists()
        playlists = [playlist for playlist in response['items']]

        plid = None
        for playlist in playlists:
            if playlist['name'] == name:
                plid = playlist['id']
                break
        if plid is None:
            user = self.client.current_user()["id"]
            plid = self.client.user_playlist_create(user, name)["id"]
        self.client.playlist_replace_items(plid, tracks)
        return True

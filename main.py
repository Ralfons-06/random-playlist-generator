import os
from spotify_client import SpotifyClient

PLAYLIST_NAME = "Weekly Rotation"


def run():
    #TODO: proper Auth
    spotify_client = SpotifyClient(os.getenv('SPOTIFY_AUTH_TOKEN'))

    playlist = spotify_client.prepare_playlist(PLAYLIST_NAME)

    random_tracks = spotify_client.get_random_tracks()
    track_ids = [track['uri'] for track in random_tracks]

    was_added_to_playlist = spotify_client.add_tracks_to_playlist(track_ids, playlist)
    if was_added_to_playlist:
        for track in random_tracks:
            print(f'Added {track["name"]} to playlist')


if __name__ == '__main__':
    run()

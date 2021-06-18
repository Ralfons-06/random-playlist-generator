from spotify_client import SpotifyClient


PLAYLIST_NAME = "WEEKLY ROTATION"


def run():
    scope = [
        "playlist-modify-public",
        "playlist-modify-private",
        "playlist-read-private",
        "playlist-read-collaborative",
        "user-library-modify",
        "user-library-read"
    ]
    client = SpotifyClient(scope)
    tracks = client.get_tracks()
    track_uris = [track['uri'] for track in tracks]
    success = client.create_random_playlist("WEEKLY ROTATION1", track_uris)
    if success:
        for track in tracks:
            print(track["name"])


if __name__ == '__main__':
    run()

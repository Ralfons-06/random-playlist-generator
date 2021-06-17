import requests
import random
import json


class SpotifyClient(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def get_random_tracks(self):
        url = f'https://api.spotify.com/v1/me/tracks'

        total_response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        total = total_response.json()['total']

        random_tracks = []
        i = 0
        while i in range(50):
            offset = random.randrange(total - 1)
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                params={
                    "limit": "1",
                    "offset": str(offset)
                }
            )

            response_json = response.json()
            track = [temp_track for temp_track in response_json['items']]

            if track not in random_tracks:
                random_tracks.append(track[0]['track'])
                i += 1

        return random_tracks

    def prepare_playlist(self, name):
        url = f'https://api.spotify.com/v1/me/playlists'
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}"
            },
            params={
                "limit": "50"
            }
        )
        response_json = response.json()
        playlists = [playlist for playlist in response_json['items']]

        plid = None
        for i in range(len(playlists)):
            if playlists[i]['name'] == name:
                plid = playlists[i]['id']
                break

        if plid is not None:
            url_playlist = f'https://api.spotify.com/v1/playlists/{plid}/tracks'
            response_get_pl = requests.get(
                url_playlist,
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                params={
                    "playlist_id": plid,
                    "market": "DE",
                    "fields": "items(track(uri))"
                }
            )

            old_tracks = response_get_pl.json()
            old_tracks['tracks'] = old_tracks.pop('items')
            for i in range(len(old_tracks['tracks'])):
                old_tracks['tracks'][i] = old_tracks['tracks'][i].pop('track')
            tracks = old_tracks['tracks']
            print(json.dumps(tracks))
            response_delete_pl = requests.delete(
                url_playlist,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                params={
                    "playlist_id": plid
                },
                json={
                    "tracks": tracks
                }
            )

            return plid
        # else:
        # TODO: create Playlist if not created yet

    def add_tracks_to_playlist(self, track_ids, playlist):
        url = f'https://api.spotify.com/v1/playlists/{playlist}/tracks'

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            params={
                "playlist_id": playlist
            },
            json={
                "uris": track_ids
            }
        )

        return response.ok

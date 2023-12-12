import os
import yaml
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth


"""
Option 1:
Import from yaml file with format:
    SPOTIPY_CLIENT_ID: 'your-spotify-client-id'
    SPOTIPY_CLIENT_SECRET: 'your-spotify-client-secret'
    SPOTIPY_REDIRECT_URI: 'your-app-redirect-url'

Option 2:
Save the following as Environment variables or import them from another file:
    
    export SPOTIPY_CLIENT_ID='your-spotify-client-id'
    export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
    export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

"""
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

SPOTIPY_CLIENT_ID = config['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = config['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI = config['SPOTIPY_REDIRECT_URI']

# username = input('Username: ')
scope = 'playlist-modify-public'

cache_path = os.getcwd() + '\.cache'

auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI, 
    scope=scope, 
    cache_path=cache_path
)

token = auth_manager.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth=token)

# # util
# try:
#     token = util.prompt_for_user_token(username=username, scope=scope)
# except:
#     os.remove(f'.cache-{username}')
#     token = util.prompt_for_user_token(username=username, scope=scope)

# sp = spotipy.Spotify(auth=token)

# SpotifyOAuth
# try:
#     auth_manager = SpotifyOAuth(username=username, scope=scope)
# except:
#     os.remove(f'.cache-{username}')
#     auth_manager = SpotifyOAuth(username=username, scope=scope)

# sp = spotipy.Spotify(auth_manager=auth_manager)


######################################################################
"""
    getting song id and uri
"""
def search_track(name: str):
    query = 'track: ' + name
    results = sp.search(q=query, limit=1, type='track')
    items = results['tracks']['items'][0]

    # track info
    track_name = items['name']
    artist = items['artists'][0]['name']
    track_id = items['id']
    uri = items['uri']
    
    return uri

track_names = ['I\'ll be home for Christmas', 'All I want for Christmas', 'Last Christmas']

track_uris = []
for name in track_names:
    uri = search_track(name=name)
    track_uris.append(uri)


######################################################################

"""
    Create playlist
"""
user_id = sp.current_user()['id']
playlist_name = input("Playlist name: ")
playlist_list = [p['name'] for p in sp.current_user_playlists()['items']]

if playlist_name not in playlist_list:
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, collaborative=False, description="this is a test")
    print('Playlist successfully created')
else:
    print("Playlist already exists")
    exit()
playlist_id = new_playlist['id']

######################################################################

"""
    add tracks
"""
sp.playlist_add_items(playlist_id=playlist_id, items=track_uris)


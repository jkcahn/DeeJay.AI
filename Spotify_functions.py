
import spotipy


class Spotify_Playlist_Creator:
    def __init__(self, auth_manager):
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        
    
    def create_playlist(self, playlist_name):
        user_id = self.sp.current_user()['id']
        playlist_list = [p['name'] for p in self.sp.current_user_playlists()['items']]

        if playlist_name not in playlist_list:
            new_playlist = self.sp.user_playlist_create(
                user=user_id, 
                name=playlist_name, 
                public=True, 
                collaborative=False, 
                description="this is a test"
            )
        else:
            return None
        
        self.playlist_id = new_playlist['id']
        
        # Get playlist url
        response = self.sp.playlist(playlist_id=self.playlist_id)
        playlist_url = response['external_urls']['spotify']
        
        return playlist_url
    
    """
    getting song id and uri
    """
    def search_track(self, song_query):
        query = 'track: ' + song_query
        results = self.sp.search(q=query, limit=1, type='track')
        items = results['tracks']['items'][0]

        # track info
        track_name = items['name']
        artist = items['artists'][0]['name']
        track_id = items['id']
        uri = items['uri']
        
        return uri

    """
    add tracks
    """
    def add_songs(self, songlist):

        track_uris = []
        for query in songlist:
            uri = self.search_track(song_query=query)
            track_uris.append(uri)

        self.sp.playlist_add_items(playlist_id=self.playlist_id, items=track_uris)


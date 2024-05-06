
import googleapiclient.discovery as gdiscovery # import build


class YouTube_Playlist_Creator:
    def __init__(self, credentials):
        
        API_SERVICE_NAME = 'youtube'
        API_VERSION = 'v3'
        
        build = gdiscovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)
        self.youtube = build
    
    def create_playlist(self):
        playlist_create_body = dict(
            snippet=dict(
                title="test playlist",
                description="test description"
            ),
            status=dict(
                privacyStatus='private'
            )
        )
        
        playlist_create_response = self.youtube.playlists().insert(
            part='snippet,status',
            body=playlist_create_body
        ).execute()
        
        self.playlist_id = playlist_create_response['id']
        
        return 'https://www.youtube.com/playlist?list=' + self.playlist_id
    
    
    def add_songs(self, songlist):
        # search through list of songs
        for song in songlist:
            
            # search for song
            search_response = self.youtube.search().list(
                q=song,
                part='snippet',
                type='video',
                videoCategoryId=10, # music category
                maxResults=1
            ).execute()
            
            # extract song data
            if 'items' in search_response:
                video = search_response['items'][0]
                video_id = video['id']['videoId']
                video_title = video['snippet']['title']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
            
            playlist_add_body = {
                "snippet": {
                    "playlistId": self.playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
            
            # add to playlist
            self.youtube.playlistItems().insert(
            part='snippet,status',
            body=playlist_add_body
            ).execute()
"""
examples for main and routes
https://github.com/hereismari/spotify-flask/blob/master/app.py
https://medium.com/analytics-vidhya/discoverdaily-a-flask-web-application-built-with-the-spotify-api-and-deployed-on-google-cloud-6c046e6e731b
    https://github.com/lucaoh21/Spotify-Discover-2.0/blob/master/routes.py
https://github.com/drshrey/spotify-flask-auth-example/blob/master/main.py


"""
import json
import flask
import secrets
import os

import google_auth_oauthlib.flow as gflow# import InstalledAppFlow
import google.oauth2.credentials as gcred
import spotipy
from spotipy.oauth2 import SpotifyOAuth


from YouTube_functions import YouTube_Playlist_Creator
from Spotify_functions import Spotify_Playlist_Creator
from Genai_functions import Genai


# load secrets and keys
with open('config.json', 'r') as f:
    config = json.load(f)

    GOOGLE_API_KEY = config.get("GOOGLE_API_KEY")

    SPOTIFY_CLIENT_ID = config.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = config.get("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = config.get("SPOTIFY_REDIRECT_URI")

    YOUTUBE_CLIENT_ID = config.get("YOUTUBE_CLIENT_ID")
    YOUTUBE_CLIENT_SECRET = config.get("YOUTUBE_CLIENT_SECRET")



YT_CONFIG = {
    "installed": {
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "redirect_uris": ["http://localhost:8080/yt-callback", "https://djai-411603.uc.r.appspot.com/yt-callback"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token"
    }
}

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/youtube', 'https://www.googleapis.com/auth/youtube.force-ssl']
SPOTIFY_SCOPE = 'playlist-modify-public'


app = flask.Flask(__name__)
app.secret_key = secrets.token_hex()
gg = Genai(GOOGLE_API_KEY=GOOGLE_API_KEY)

"""--------------------------------FLASK FUNCTIONS--------------------------------"""
def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


"""--------------------------------HOMEPAGE--------------------------------"""
@app.route('/', methods=['GET', 'POST'])
def index():
    if flask.request.method == "POST":
        flask.session['playlist_name'] = flask.request.form.get('playlist_name')
        flask.session['playlist_input'] = flask.request.form.get('input')
        flask.session['num_songs'] = flask.request.form.get('song_counter')
        
        return flask.redirect('loading')
    else:
        if 'songlist' in flask.session:
            songlist = flask.session['songlist']

            return flask.render_template('index.html', 
                                  song_results=songlist,
                                  returnMessage="Here is your playlist!"
            )
        else:
            return flask.render_template('index.html')

@app.route('/loading')
def loading():
    return flask.render_template('loading.html')

@app.route('/process')
def process():    
    if 'playlist_input' in flask.session and 'num_songs' in flask.session:
        playlist_input = flask.session['playlist_input']
        num_songs = flask.session['num_songs']

        songlist = gg.playlist_request(playlist_input=playlist_input, num_songs=num_songs)
        if not songlist:
            return flask.render_template('index.html', error="Input not accepted")
        
        flask.session['songlist'] = songlist
    
    return flask.redirect(flask.url_for('index'))

@app.route('/clear')
def clear():
    if 'playlist_name' in flask.session:
        flask.session.pop('playlist_name')
    if 'songlist' in flask.session:
        flask.session.pop('songlist')
    
    return flask.redirect(flask.url_for('index'))


"""--------------------------------SP AUTH--------------------------------"""
"""
https://github.com/lucaoh21/Spotify-Discover-2.0/blob/master/routes.py
https://github.com/spotipy-dev/spotipy/blob/master/examples/app.py
Called by the backend when a user has not authorized the application to
access their Spotify account. Attempts to authorize a new user by redirecting
them to the Spotify authorization page.
"""
@app.route('/sp-authorize')
def sp_authorize():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(flask.session)
    
    # redirect user to Spoitfy authorization page
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_handler=cache_handler
    )
    
    return flask.redirect(auth_manager.get_authorize_url())


"""
Called after a new user has authorized the application through the Spotify API page.
Stores user information in a session and redirects user back to the page they initally
attempted to visit.
"""
@app.route('/sp-callback')
def callback():
    """
    validate token and redirect to test
    """
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(flask.session)
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_handler=cache_handler
    )
    
    # Get access code after redirect
    auth_manager.get_access_token(flask.request.args.get('code'))
    
    # Check token
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return flask.render_template('index.html', error='Auth failed. ')
    
    
    return flask.redirect(flask.url_for('sp_request'))

"""--------------------------------YT AUTH--------------------------------"""
"""
https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps
"""

@app.route('/yt-authorize')
def yt_authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = gflow.InstalledAppFlow.from_client_config(client_config=YT_CONFIG, scopes=GOOGLE_SCOPES)

    # URI must match redirect uri in API console for app
    # set redirecut_uri for authorization url
    flow.redirect_uri = flask.url_for('yt_callback', _external=True)

    authorization_url, yt_state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['yt_state'] = yt_state

    return flask.redirect(authorization_url)


@app.route('/yt-callback')
def yt_callback():

    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    if "yt_state" not in flask.session:
        return flask.render_template('index.html', error="State unavailable. Retry Youtube")
    
    yt_state = flask.session['yt_state']

    flow = gflow.InstalledAppFlow.from_client_config(client_config=YT_CONFIG, scopes=GOOGLE_SCOPES, state=yt_state)
    flow.redirect_uri = flask.url_for('yt_callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    yt_credentials = flow.credentials
    flask.session['yt_credentials'] = credentials_to_dict(yt_credentials)

    return flask.redirect(flask.url_for('yt_request'))



"""--------------------------------API REQUEST--------------------------------"""

@app.route('/youtube')
def yt_request():
    # check if songlist has been generated
    if 'songlist' not in flask.session:
        return flask.render_template('index.html', error="Please offer input to generate a playlist")
    else:
        songlist = flask.session['songlist']
    
    # check if user has input playlist name
    if 'playlist_name' not in flask.session:
        return flask.render_template('index.html', error="Please specify playlist name")
    else:
        playlist_name = flask.session['playlist_name']
    
    
    if 'yt_credentials' not in flask.session:
        return flask.redirect('yt-authorize')

    # Load credentials from the session.
    yt_credentials = gcred.Credentials(
        **flask.session['yt_credentials'])
    
    youtube = YouTube_Playlist_Creator(credentials=yt_credentials)
    yt_playlist_url = youtube.create_playlist(playlist_name=playlist_name)
    youtube.add_songs(songlist=songlist)

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['yt_credentials'] = credentials_to_dict(yt_credentials)

    return flask.render_template(
        'index.html',
        song_results=songlist,
        yt_playlist_url=yt_playlist_url
    )



@app.route('/spotify')
def sp_request():
    # check if songlist has been generated
    if 'songlist' not in flask.session:
        return flask.render_template('index.html', error="Please offer input to generate a playlist")
    else:
        songlist = flask.session['songlist']
    
    # check if user has input playlist name
    if 'playlist_name' not in flask.session:
        return flask.render_template('index.html', error="Please specify playlist name")
    else:
        playlist_name = flask.session['playlist_name']
    
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(flask.session)
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_handler=cache_handler
    )
    
    # validate token automatically refreshes access_token
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return flask.redirect('sp-authorize')
    
    sp = Spotify_Playlist_Creator(auth_manager=auth_manager)
    sp_playlist_url = sp.create_playlist(playlist_name=playlist_name)
    sp.add_songs(songlist=songlist)
    
    return flask.render_template(
        'index.html',
        songs_results=songlist,
        sp_playlist_url=sp_playlist_url
    )


"""
running locally
"""
if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)
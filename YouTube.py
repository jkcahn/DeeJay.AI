import google.generativeai as genai
import json
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

# load secrets and keys
with open("secrets.json", "r") as f:
    secrets = json.load(f)

    GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]

    SPOTIPY_CLIENT_ID = secrets["SPOTIPY_CLIENT_ID"]
    SPOTIPY_CLIENT_SECRET = secrets["SPOTIPY_CLIENT_SECRET"]
    SPOTIPY_REDIRECT_URI = secrets["SPOTIPY_REDIRECT_URI"]

    YOUTUBE_CLIENT_ID = secrets["YOUTUBE_CLIENT_ID"]
    YOUTUBE_CLIENT_SECRET = secrets["YOUTUBE_CLIENT_SECRET"]


# """GOOGLE GENAI"""

# genai.configure(api_key=GOOGLE_API_KEY)

# # Set up the model
# generation_config = {
#   "temperature": 0.5,
#   "top_p": 1,
#   "top_k": 1,
#   "max_output_tokens": 2048,
# }

# safety_settings = [
#   {
#     "category": "HARM_CATEGORY_HARASSMENT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_HATE_SPEECH",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   }
# ]

# model = genai.GenerativeModel(model_name="gemini-pro",
#                               generation_config=generation_config,
#                               safety_settings=safety_settings)

# prompt_parts = [
#   "Can you make a playlist for reading a book on the couch on a rainy day? \
#   Format it like this:\
#   1. (Song title) - (Artist name) \
#   2. (Song title) - (Artist name) \
#   *",
# ]

# response = model.generate_content(prompt_parts)
# # print(response.text)

# # Formatting response
# response_list = response.text.strip().split('\n')
# songlist = []
# for string in response_list:
#     if string:
#         string = string[string.find(next(filter(str.isalpha, string))):]
#         if '\"' in string:
#             string = string.replace('\"', '')
#         songlist.append(string)



"""YOUTUBE WITH DATA API"""

import os
import flask
import requests
import secrets

import google_auth_oauthlib.flow as gflow# import InstalledAppFlow
import google.auth.transport.requests # import Request
import googleapiclient.discovery as gdiscovery # import build
import google.oauth2.credentials as gcred


CLIENT_CONFIG = {
    "installed": {
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token"
    }
}

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = flask.Flask(__name__)
app.secret_key = secrets.token_hex()

# flow = gflow.InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
# flow.run_local_server(host='localhost', port=5000)
# credentials = flow.credentials


# youtube = gdiscovery.build("youtube", "v3", credentials=credentials)

# request = youtube.playlistItems().list(
#     part="status", playlistId="PLNnanoZ0SYbT__U739deCE30RjzeDwcur"
# )

# response = request.execute()

# print(response)




@app.route('/')
def index():
    return print_index_table()


@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = gcred.Credentials(
        **flask.session['credentials'])

    youtube = gdiscovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    search_response = youtube.search().list(
        q="so good johnny stimson",
        part='snippet',
        type='video',
        videoCategoryId=10, # music category
        maxResults=1
    ).execute()

    if 'items' in search_response:
        video = search_response['items'][0]
        video_id = video['id']['videoId']
        video_title = video['snippet']['title']
        video_url = f'https://www.youtube.com/watch?v={video_id}'

    playlist_create_body = dict(
        snippet=dict(
            title="test playlist",
            description="test description"
        ),
        status=dict(
            privacyStatus='private'
        )
    )
        
    playlist_create_response = youtube.playlists().insert(
        part='snippet,status',
        body=playlist_create_body
    ).execute()
    playlist_id = playlist_create_response['id']

    playlist_add_body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
            }
        }
    }

    plalist_add_response = youtube.playlistItems().insert(
        part='snippet,status',
        body=playlist_add_body
    ).execute()



    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.jsonify(**plalist_add_response)


@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = gflow.InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)

    # URI must match redirect uri in API console for app
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():

    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = gflow.InstalledAppFlow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())
    else:
        return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return ('Credentials have been cleared.<br><br>' +
            print_index_table())


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)
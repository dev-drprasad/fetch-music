# serve.py
import binascii
from pprint import pprint
from StringIO import StringIO
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from mutagen.id3 import ID3, TIT2, TALB, TPE1, COMM, TCON, APIC
import requests
import spotipy

MPL_SEARCH_API = 'http://databrainz.com/api/search_api.cgi'
MPL_DATA_API = 'http://databrainz.com/api/data_api_new.cgi'
MPL_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'http://musicpleer.audio/'
}

app = Flask(__name__)
CORS(app)

def xorWord(text, key):
    # https://stackoverflow.com/questions/2612720/how-to-do-bitwise-exclusive-or-of-two-strings-in-python
    # https://stackoverflow.com/questions/6624453/whats-the-correct-way-to-convert-bytes-to-a-hex-string-in-python-3
    bytes_string = ''.join(chr(ord(s)^ord(c)) for s,c in zip(text,key*100))
    return binascii.hexlify(bytes_string.encode('utf8'))

# a route which servers index page
@app.route('/')
def index():
    return '<html><body>Welcome to fetch music app.</body></html>'

@app.route('/api/search')
def search():
    response = {}
    if 'q' in request.args:
        search_term = request.args.get('q')

        mpl_search_params = dict(qry=search_term, jsoncallback='', format='json', mh=50, where='mpl')
        search_response = requests.get(MPL_SEARCH_API, headers=MPL_HEADERS, params=mpl_search_params)
        results = search_response.json().get('results', []) if search_response.content else []

        response['results'] = results
        json_response = jsonify(response)
        json_response.status_code = 200
        return json_response
    else:
        response['error'] = 'no `q` parameter found in url'
        json_response = jsonify(response)
        json_response.status_code = 400
        return json_response

    return jsonify(response)

@app.route('/api/song')
def fetch_song_location():
    response = {}
    if 'id' in request.args:
        song_id = request.args.get('id')
        encrypted_id = xorWord(song_id, 'mpl')

        print('hitting ' + MPL_DATA_API.format(encrypted_id))

        mpl_data_params = dict(id=encrypted_id, jsoncallback='', r='mpl', format='json')
        src_response = requests.get(MPL_DATA_API, headers=MPL_HEADERS, params=mpl_data_params)
        print src_response.content
        song_details = src_response.json().get('song', {}) if src_response.content else {}
        response['song'] = song_details
        song_title = song_details.get('title')
        audio_response = requests.get(song_details.get('url'))
        print('writing audio file')
        with open(song_title + '.mp3', 'w') as file:
            file.write(audio_response.content)

        from spotipy.oauth2 import SpotifyClientCredentials
        client_credentials_manager = SpotifyClientCredentials()
        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        spotify_results = spotify.search(q=song_details.get('title', '') + ' ' + song_details.get('artist', ''), type='track')
        track_info = spotify_results['tracks']['items'][0]
        track_title = track_info.get('name')
        track_album = track_info.get('album').get('name')
        track_artists = track_info.get('artists')[0].get('name')
        track_image = track_info.get('album').get('images')[0].get('url')
        image_response = requests.get(track_image)
        with open('image.jpg', 'wb') as f:
            f.write(image_response.content)
        track_number = track_info.get('track_number')
        print track_number, track_album, track_artists, track_image
        audio = ID3(song_title + '.mp3')
        audio.add(TIT2(encoding=3, text=track_title))
        audio.add(TALB(encoding=3, text=track_album))
        audio.add(TPE1(encoding=3, text=track_artists))
        audio.add(TCON(encoding=3, text=str(track_number)))
        audio.add(COMM(encoding=3, lang=u'eng', desc='', text=u''))
        with open('image.jpg', 'rb') as f:
            image_data = f.read()
            audio.add(APIC(3, 'image/jpeg', 3, 'Cover', image_data))
        audio.save()
        json_response = jsonify(response)
        json_response.status_code = 200
        print('returning file')
        return send_file('../' + song_title + '.mp3')
    else:
        response['error'] = 'no `id` parameter found in url'
        json_response = jsonify(response)
        json_response.status_code = 400
        return json_response

    return jsonify(response)
# run the application
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)

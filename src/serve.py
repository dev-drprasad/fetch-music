# serve.py
import binascii
import json
import logging
from io import BytesIO
from pprint import pprint
from urllib.request import urlopen
import re

from flask import Flask, Response,render_template, jsonify, request, send_file
from flask_cors import CORS
from mutagen.id3 import ID3, TIT2, TALB, TPE1, COMM, TCON, APIC
from mutagen.id3._util import error
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

def add_metadata(chunk, song_details):
    io_chunk = BytesIO(chunk)
    is_chunk_enough = False
    try:
        audio = ID3(io_chunk)
        is_chunk_enough = True
    except error:
        return is_chunk_enough, None
    
    app.logger.info('adding new metadata...')
    from spotipy.oauth2 import SpotifyClientCredentials
    client_credentials_manager = SpotifyClientCredentials()
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    q = song_details.get('title', '') + ' ' + song_details.get('artist').split()[0] if song_details.get('artist').split() else ''
    app.logger.info('spotify q: ' + q)
    spotify_results = spotify.search(q=q, type='track')
    track_info = spotify_results['tracks']['items'][0]
    track_title = track_info.get('name')
    track_album = track_info.get('album').get('name')
    track_artists = track_info.get('artists')[0].get('name')
    
    
    track_number = track_info.get('track_number')
    # app.logger.info track_number, track_album, track_artists, track_image
    # audio = ID3(song_title + '.mp3')
    
    audio.add(TIT2(encoding=3, text=track_title))
    audio.add(TALB(encoding=3, text=track_album))
    audio.add(TPE1(encoding=3, text=track_artists))
    audio.add(TCON(encoding=3, text=str(track_number)))
    audio.add(COMM(encoding=3, lang=u'eng', desc='', text=u''))
    

    # artist_id = track_info.get('artists')[0].get('id')
    # if artist_id:
    #     app.logger.info('artist name: {}, artist id: {}'.format(track_artists, artist_id))
    #     artist_info = spotify.artist(artist_id)
    #     artist_image_url = artist_info.get('images')[2].get('url')
    #     app.logger.info('artist image: {}'.format(artist_image_url))
    #     artist_image_resp = urlopen(artist_image_url)
    #     artist_image_bytes = artist_image_resp.read()
    #     audio.add(APIC(3, 'image/png', 7, '', artist_image_bytes))
    track_image = track_info.get('album').get('images')[0].get('url')
    app.logger.info('image: ' + track_image)
    image_response = urlopen(track_image)
    image_bytes = image_response.read()
    audio.add(APIC(3, 'image/png', 3, '', image_bytes))
    
    io_chunk.seek(0)
    old_size, new_data_bytes = audio.new_data(io_chunk)
    if old_size > 300000:
        app.logger.warning('old size greater than 300KB. value: {}'.format(old_size))
    app.logger.info('old size: {}'.format(old_size))
    return is_chunk_enough, new_data_bytes + chunk[old_size:]

# a route which servers index page
@app.route('/')
def index():
    return '<html><body>Welcome to fetch music app.</body></html>'

@app.route('/api/search')
def search():
    response = {}
    if 'q' in request.args:
        search_term = request.args.get('q')

        mpl_search_params = dict(
            qry=search_term,
            jsoncallback='jQuery1111019191608358321144_1513422008666',
            format='json', mh=50, where='mpl'
        )
        search_response = requests.get(MPL_SEARCH_API, headers=MPL_HEADERS, params=mpl_search_params)
        content = search_response.text
        if content:
            match = ''.join(re.findall(r'({.*})', content, re.DOTALL))
            json_response = json.loads(match)
            results = json_response.get('results', []) if search_response.content else []
        else:
            results = []
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

        app.logger.info('hitting ' + MPL_DATA_API.format(encrypted_id))

        mpl_data_params = dict(id=encrypted_id, jsoncallback='jQuery1111019191608358321144_1513422008666',
        r='mpl',
        format='json')
        src_response = requests.get(MPL_DATA_API, headers=MPL_HEADERS, params=mpl_data_params)
        # app.logger.info(src_response.content)
        content = src_response.text
        match = ','.join(re.findall(r'({.*})', content))
        json_response = json.loads(match)
        song_details = json_response.get('song', {}) if src_response.content else {}
        response['song'] = song_details
        song_title = song_details.get('title')
        # audio_response = requests.get(song_details.get('url'))
        # app.logger.info('writing audio file')
        # with open(song_title + '.mp3', 'wb') as file:
        #     file.write(audio_response.content)
        def generate(url):
            app.logger.info('audio link: {}'.format(url))
            audio_response = urlopen(url)
            # app.logger.info('getting first 350KB')
            # chunk = audio_response.read(1024 * 350)
            chunk = b''
            processed_chunk = None
            while True:
                app.logger.info('read chunk size of 200KB')
                chunk += audio_response.read(1024 * 200)
                is_chunk_enough, processed_chunk = add_metadata(
                    chunk, song_details)
                if is_chunk_enough:
                    break
            while processed_chunk:
                yield processed_chunk
                processed_chunk = audio_response.read(1024 * 100)

        json_response = jsonify(response)
        json_response.status_code = 200
        app.logger.info('returning file')
        # return send_file('../' + song_title + '.mp3')
        return Response(
            generate(song_details.get('url')),
            mimetype='audio/mpeg3',
            headers={"Content-Disposition":'attachment;filename={}.mp3'.format(song_title)}
        )
    else:
        response['error'] = 'no `id` parameter found in url'
        json_response = jsonify(response)
        json_response.status_code = 400
        return json_response

    return jsonify(response)
# run the application
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8081)

# References:
# https://docs.python.org/3/library/io.html
# https://stackoverflow.com/questions/1517616/stream-large-binary-files-with-urllib2-to-file
# https://stackoverflow.com/questions/34349699/when-streaming-response-in-flask-file-unplayable
# https://gist.github.com/hosackm/289814198f43976aff9b

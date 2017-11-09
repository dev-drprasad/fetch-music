# serve.py
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests

# creates a Flask application, named app
app = Flask(__name__, template_folder='../build/', static_folder='../build/static')
CORS(app)
# a route which servers index page
@app.route('/')
def index():
    return '<html><body>Welcome to fetch music app.</body></html>'

@app.route('/api/search')
def search():
    response = {}
    if 'q' in request.args:
        search_term = request.args.get('q')
        src_response = requests.get('http://databrainz.com/api/search_api.cgi?jsoncallback=&qry={}&format=json&mh=50&where=mpl'.format(search_term))
        results = src_response.json().get('results', []) if src_response.content else []
        response['results'] = results
        json_response = jsonify(response)
        json_response.status_code = 200
        return json_response
    else:
        response['error'] = 'no `q` parameter found in url'
        json_response = jsonify(response)
        json_response.status_code = 400

    return jsonify(response)

# run the application
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)

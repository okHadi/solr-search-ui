from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
SOLR_URL = 'http://localhost:8983/solr/books/select'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '*:*')
    category = request.args.get('category', '')
    author = request.args.get('author', '')

    params = {
        'q': f'title:{query}' if query else '*:*',
        'wt': 'json',
        'rows': 20,
        'q.op': 'OR',
        'indent': 'true',
    }

    fq = []
    if category:
        fq.append(f'category:{category}')
    if author:
        fq.append(f'author:"{author}"')
    if fq:
        params['fq'] = fq

    try:
        response = requests.get(SOLR_URL, params=params)
        response.raise_for_status()
        docs = response.json()['response']['docs']
        return jsonify(docs)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '')
    params = {
        'q': f'title:{query}*',
        'wt': 'json',
        'rows': 5,
        'fl': 'title',
        'q.op': 'OR',
        'indent': 'true'
    }

    try:
        response = requests.get(SOLR_URL, params=params)
        response.raise_for_status()
        docs = response.json()['response']['docs']
        suggestions = [doc['title'] for doc in docs]
        return jsonify(suggestions)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

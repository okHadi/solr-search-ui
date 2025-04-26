from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
SOLR_URL = 'http://localhost:8983/solr/books/select'  # Adjusted the Solr URL


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    # Default to all documents if no query is provided
    query = request.args.get('q', '*:*')
    category = request.args.get('category', '')
    author = request.args.get('author', '')

    params = {
        # Search in the title field for the query
        'q': f'title:{query}' if query else '*:*',
        'wt': 'json',  # Response in JSON format
        'rows': 20,  # Limit the number of results to 20
        'q.op': 'OR',  # Default query operator
        'indent': 'true',  # Indent the JSON response for readability
    }

    # Apply filters for category and author if provided
    fq = []
    if category:
        fq.append(f'category:{category}')
    if author:
        fq.append(f'author:"{author}"')
    if fq:
        params['fq'] = fq

    try:
        response = requests.get(SOLR_URL, params=params)
        response.raise_for_status()  # Raise an error if the request fails
        # Extract documents from the response
        docs = response.json()['response']['docs']
        return jsonify(docs)  # Return the results as JSON
    except requests.exceptions.RequestException as e:
        # Return an error message if the request fails
        return jsonify({"error": str(e)}), 500


@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '')  # Get the query for autocomplete
    params = {
        'q': f'title:{query}*',  # Search for titles starting with the query
        'wt': 'json',  # Response in JSON format
        'rows': 5,  # Limit to 5 results for autocomplete suggestions
        'fl': 'title',  # Only return the title field
        'q.op': 'OR',  # Query operator
        'indent': 'true'  # Indent the JSON response for readability
    }

    try:
        response = requests.get(SOLR_URL, params=params)
        response.raise_for_status()  # Raise an error if the request fails
        # Extract documents from the response
        docs = response.json()['response']['docs']
        suggestions = [doc['title']
                       for doc in docs]  # Extract titles for suggestions
        return jsonify(suggestions)  # Return the suggestions as JSON
    except requests.exceptions.RequestException as e:
        # Return an error message if the request fails
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Reddit JSON Proxy</h1>
    <p>Usage: Pass a Reddit URL as the <code>url</code> query parameter.</p>
    <p>Example: <code>/?url=https://www.reddit.com/r/AZURE/comments/1g0mkwi/title_unexpected_50k_azure_bill_for_openai</code></p>
    '''

@app.route('/fetch')
def fetch_reddit():
    url = request.args.get('url')

    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400

    # Validate it's a Reddit URL
    if not re.match(r'^https?://(www\.|old\.)?reddit\.com/', url):
        return jsonify({'error': 'Not a valid Reddit URL'}), 400

    # Remove trailing slash if present
    url = url.rstrip('/')

    # Remove .json if already present (to avoid .json.json)
    if url.endswith('.json'):
        url = url[:-5]

    # Use old.reddit.com - more permissive with automated requests
    url = re.sub(r'https?://(www\.)?reddit\.com', 'https://old.reddit.com', url)

    # Append .json
    json_url = url + '.json'

    try:
        # Use a session to handle cookies
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        session.headers.update(headers)

        # First request to get cookies
        session.get('https://old.reddit.com', timeout=10)

        # Now fetch the JSON
        resp = session.get(json_url, timeout=10)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

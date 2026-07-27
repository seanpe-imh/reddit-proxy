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
    if not re.match(r'^https?://(www\.)?reddit\.com/', url):
        return jsonify({'error': 'Not a valid Reddit URL'}), 400
    
    # Remove trailing slash if present
    url = url.rstrip('/')
    
    # Remove .json if already present (to avoid .json.json)
    if url.endswith('.json'):
        url = url[:-5]
    
    # Append .json
    json_url = url + '.json'
    
    try:
        resp = requests.get(
            json_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            },
            timeout=10
        )
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

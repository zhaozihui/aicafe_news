from flask import Flask, jsonify, render_template, request, send_from_directory
import feedparser
import os
import time
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
FEED_URLS = {
    'artificial_intelligence': 'https://www.google.com/alerts/feeds/17855623974115894960/6097938762894236885',
    'ChatGPT': 'https://www.google.com/alerts/feeds/17855623974115894960/7762526077996380983',
    'OpenAI': 'https://www.google.com/alerts/feeds/17855623974115894960/16580318526471445446'
}

CACHE_DIR = 'cache'
CACHE_DURATION = 3600  # 缓存持续时间为1小时

def get_cache_filename(topic):
    return os.path.join(CACHE_DIR, f'{topic}.json')

def is_cache_valid(filename):
    if not os.path.exists(filename):
        return False
    cache_time = os.path.getmtime(filename)
    current_time = time.time()
    return (current_time - cache_time) < CACHE_DURATION

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/feed/<topic>')
def get_feed(topic):
    cache_file = get_cache_filename(topic)
    
    # 检查缓存是否有效
    if is_cache_valid(cache_file):
        with open(cache_file, 'r') as f:
            feed_data = json.load(f)
    else:
        rss_url = FEED_URLS.get(topic)
        if not rss_url:
            return jsonify({'error': 'Invalid topic'}), 400
        feed = feedparser.parse(rss_url)
        feed_data = {
            'title': feed.feed.title,
            'entries': [
                {
                    'id': entry.id,
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'updated': entry.updated,
                    'content': entry.content[0].value if 'content' in entry else entry.summary
                }
                for entry in feed.entries
            ]
        }
        # 保存缓存
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(feed_data, f)
    
    return jsonify(feed_data)

if __name__ == '__main__':
    app.run(debug=False, port=5000)

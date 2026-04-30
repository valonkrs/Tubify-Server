from flask import Flask, jsonify
import subprocess
import sys
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'status': 'ok', 'service': 'tubify'})

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/audio/<video_id>')
def get_audio(video_id):
    try:
        result = subprocess.run([
            sys.executable, '-m', 'yt_dlp',
            '--no-playlist',
            '-f', 'bestaudio/best',
            '--get-url',
            '--no-check-certificate',
            '--extractor-args', 'youtube:skip=dash,hls',
            f'https://www.youtube.com/watch?v={video_id}'
        ], capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return jsonify({'error': result.stderr}), 400

        url = result.stdout.strip().split('\n')[0]
        if not url:
            return jsonify({'error': 'No URL found'}), 400

        return jsonify({'url': url})

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timeout'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

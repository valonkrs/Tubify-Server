from flask import Flask, jsonify
import subprocess
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
            'yt-dlp',
            '--no-playlist',
            '-f', 'bestaudio',
            '--get-url',
            f'https://www.youtube.com/watch?v={video_id}'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return jsonify({'error': 'Could not fetch audio'}), 400
        
        url = result.stdout.strip()
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

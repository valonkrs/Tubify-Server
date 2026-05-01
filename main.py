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

@app.route('/debug')
def debug():
    # Gjej deno
    deno_which = subprocess.run(['which', 'deno'], capture_output=True, text=True)
    deno_version = subprocess.run(['deno', '--version'], capture_output=True, text=True)
    path_env = os.environ.get('PATH', '')
    cookies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')
    cookies_exists = os.path.exists(cookies_path)
    
    return jsonify({
        'deno_path': deno_which.stdout.strip(),
        'deno_version': deno_version.stdout.strip(),
        'path': path_env,
        'cookies_exists': cookies_exists,
        'cookies_path': cookies_path
    })

@app.route('/audio/<video_id>')
def get_audio(video_id):
    try:
        cookies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')
        deno_which = subprocess.run(['which', 'deno'], capture_output=True, text=True)
        deno_path = deno_which.stdout.strip()

        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--no-playlist',
            '-f', 'bestaudio/best',
            '--get-url',
            '--no-check-certificate',
            '--js-runtimes', f'deno:{deno_path}' if deno_path else 'deno',
            '--cookies', cookies_path,
            f'https://www.youtube.com/watch?v={video_id}'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

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
